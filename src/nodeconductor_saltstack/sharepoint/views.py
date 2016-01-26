from rest_framework import decorators, exceptions, mixins, response, viewsets, status
from rest_framework.status import HTTP_200_OK

from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure import views as structure_views
from nodeconductor_saltstack.saltstack.views import track_exceptions

from ..saltstack.backend import SaltStackBackendError
from . import models, serializers, tasks, filters


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.SharepointTenant.objects.all()
    serializer_class = serializers.TenantSerializer
    filter_class = filters.TenantFilter

    def perform_provision(self, serializer):
        user_count = serializer.validated_data.pop('user_count')
        storage = serializer.validated_data.pop('storage')
        tenant = serializer.save()

        tenant.set_quota_limit(tenant.Quotas.user_count, user_count)
        tenant.set_quota_limit(tenant.Quotas.storage, storage)

        backend = tenant.get_backend()
        backend.provision(tenant)

    def get_serializer_class(self):
        serializer_class = super(TenantViewSet, self).get_serializer_class()
        if self.action == 'initialize':
            serializer_class = serializers.MainSiteCollectionSerializer
        return serializer_class

    @decorators.detail_route(methods=['post'])
    def initialize(self, request, **kwargs):
        tenant = self.get_object()
        if tenant.initialization_status != models.SharepointTenant.InitializationStatuses.NOT_INITIALIZED:
            raise IncorrectStateException("Tenant must be in 'Not initialized' state to perform initialization operation.")

        # create main site collection
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        storage = serializer.validated_data.pop('storage')
        template = serializer.validated_data.pop('template')
        user = serializer.validated_data.pop('user')
        name = serializer.validated_data.pop('name')
        description = serializer.validated_data.pop('description')

        if user.tenant != tenant:
            return response.Response(
                {'user': 'User has to be from initializing tenant'}, status=status.HTTP_400_BAD_REQUEST)

        tenant.initialization_status = models.SharepointTenant.InitializationStatuses.INITIALIZING
        tenant.save()

        tasks.initialize_tenant.delay(tenant.uuid.hex, template.uuid.hex, user.uuid.hex, storage, name, description)

        return response.Response({'status': 'Initialization was scheduled successfully.'}, status=status.HTTP_200_OK)


class TemplateViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    lookup_field = 'uuid'


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_class = filters.UserFilter
    lookup_field = 'uuid'

    def perform_create(self, serializer):
        tenant = serializer.validated_data['tenant']
        backend = tenant.get_backend()

        if tenant.state != models.SharepointTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be online to perform user creation")

        try:
            backend_user = backend.users.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'])

        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            user = serializer.save()
            user.password = backend_user.password
            user.admin_id = backend_user.admin_id
            user.backend_id = backend_user.id
            user.save()

    def perform_update(self, serializer):
        user = self.get_object()
        backend = user.tenant.get_backend()

        try:
            new_password = serializer.validated_data.get('password', None)
            if new_password and user.password != new_password:
                backend.users.change_password(id=user.backend_id, password=new_password)

            changed = {k: v for k, v in serializer.validated_data.items()
                       if v and getattr(user, k) != v and k != 'password'}
            backend.users.change(admin_id=user.admin_id, **changed)

        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            serializer.save()

    def perform_destroy(self, user):
        backend = user.tenant.get_backend()
        try:
            backend.users.delete(id=user.backend_id)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            user.delete()

    # XXX: put was added as portal has a temporary bug with widget update
    @decorators.detail_route(methods=['post', 'put'])
    @track_exceptions
    def password(self, request, pk=None, **kwargs):
        user = self.get_object()
        backend = user.tenant.get_backend()
        new_password = backend.users.reset_password(id=user.backend_id)
        user.password = new_password.password
        user.save()
        data = serializers.UserPasswordSerializer(instance=user, context={'request': request}).data
        return response.Response(data, status=HTTP_200_OK)


class SiteCollectionViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):

    queryset = models.SiteCollection.objects.all()
    serializer_class = serializers.SiteCollectionSerializer
    filter_class = filters.SiteCollectionFilter
    lookup_field = 'uuid'

    def perform_create(self, serializer):
        user = serializer.validated_data['user']
        template = serializer.validated_data.pop('template')
        backend = user.tenant.get_backend()

        if user.tenant.state != models.SharepointTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform site collection creation")

        try:
            storage = serializer.validated_data.pop('storage')
            backend_site = backend.site_collections.create(
                admin_id=user.admin_id,
                template_code=template.code,
                site_url=serializer.validated_data['site_url'],
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                storage=storage)

        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            site_collection = serializer.save()
            site_collection.access_url = backend_site.url
            site_collection.save()
            site_collection.set_quota_limit(site_collection.Quotas.storage, storage)
            user.tenant.add_quota_usage(models.SharepointTenant.Quotas.storage, storage)

    def perform_destroy(self, site_collection):
        tenant = site_collection.user.tenant
        if site_collection in tenant.get_default_site_collections():
            raise exceptions.PermissionDenied(
                'It is impossible to delete default tenant site collections.')
        backend = site_collection.user.tenant.get_backend()
        try:
            backend.site_collections.delete(url=site_collection.access_url)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            site_collection.delete()
