from rest_framework import decorators, exceptions, mixins, response, viewsets
from rest_framework.status import HTTP_200_OK

from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure import views as structure_views
from nodeconductor_saltstack.saltstack.views import track_exceptions

from ..saltstack.backend import SaltStackBackendError
from . import models, serializers, filters


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.SharepointTenant.objects.all()
    serializer_class = serializers.TenantSerializer
    filter_class = filters.TenantFilter

    def perform_provision(self, serializer):
        storage = serializer.validated_data.pop('storage')
        site_name = serializer.validated_data.pop('site_name')
        site_description = serializer.validated_data.pop('site_description')
        template = serializer.validated_data.pop('template')
        phone = serializer.validated_data.pop('phone', None)
        notify = serializer.validated_data.pop('notify', None)

        tenant = serializer.save()
        tenant.set_quota_limit(tenant.Quotas.storage, storage)

        backend = tenant.get_backend()
        backend.provision(
            tenant, site_name=site_name, site_description=site_description, template_uuid=template.uuid.hex,
            phone=phone, notify=notify)

    @decorators.detail_route(methods=['post', 'put'])
    @track_exceptions
    def change_quotas(self, request, pk=None, **kwargs):
        tenant = self.get_object()
        serializer = serializers.TenantQuotaSerializer(data=request.data, context={'tenant': tenant})
        serializer.is_valid(raise_exception=True)
        tenant.set_quota_limit(models.SharepointTenant.Quotas.storage, serializer.validated_data['storage'])
        return response.Response({'status': 'Quotas were successfully changed.'}, status=HTTP_200_OK)


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

        try:
            backend_user = backend.users.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                username=serializer.validated_data['username'],
                name=serializer.validated_data['name'],
                email=serializer.validated_data['email'])

        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            # create user
            user = serializer.save()
            user.password = backend_user.password
            user.admin_id = backend_user.admin_id
            user.backend_id = backend_user.id
            # create initial site collection
            user.init_personal_site_collection(backend_user.personal_site_collection_url)

    def perform_update(self, serializer):
        user = self.get_object()
        backend = user.tenant.get_backend()

        try:
            changed = {k: v for k, v in serializer.validated_data.items() if v and getattr(user, k) != v}
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

    def get_serializer_class(self):
        serializer_class = super(SiteCollectionViewSet, self).get_serializer_class()
        if self.action == 'change_quotas':
            serializer_class = serializers.SiteCollectionQuotaSerializer
        return serializer_class

    def perform_create(self, serializer):
        user = serializer.validated_data['user']
        template = serializer.validated_data['template']
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
        if not site_collection.deletable:
            raise exceptions.PermissionDenied(
                'It is impossible to delete default tenant site collections.')
        backend = site_collection.user.tenant.get_backend()
        try:
            backend.site_collections.delete(url=site_collection.access_url)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            site_collection.delete()

    # XXX: put was added as portal has a temporary bug with widget update
    @decorators.detail_route(methods=['post', 'put'])
    @track_exceptions
    def change_quotas(self, request, pk=None, **kwargs):
        site_collection = self.get_object()
        backend = site_collection.user.tenant.get_backend()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={'site_collection': site_collection})
        serializer.is_valid(raise_exception=True)

        new_storage = serializer.validated_data['storage']
        old_storage = site_collection.quotas.get(name=models.SiteCollection.Quotas.storage).limit

        backend.site_collections.set_storage(url=site_collection.access_url, storage=new_storage)
        site_collection.set_quota_limit(models.SiteCollection.Quotas.storage, new_storage)
        tenant = site_collection.user.tenant
        tenant.add_quota_usage(models.SharepointTenant.Quotas.storage, new_storage - old_storage)

        return response.Response('Storage quota was successfully changed.', status=HTTP_200_OK)
