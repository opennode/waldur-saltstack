from rest_framework import decorators, exceptions, mixins, response, viewsets, status

from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure import views as structure_views

from ..saltstack.backend import SaltStackBackendError
from . import models, serializers


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.SharepointTenant.objects.all()
    serializer_class = serializers.TenantSerializer
    http_method_names = ['head', 'get', 'post', 'delete']

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            template=serializer.validated_data['template'],
            storage_size=serializer.validated_data['storage_size'],
            users_count=serializer.validated_data['users_count'])

    @decorators.detail_route(methods=['post'])
    def set_quotas(self, request, **kwargs):
        if not request.user.is_staff:
            raise exceptions.PermissionDenied()

        tenant = self.get_object()
        if tenant.state != models.SharepointTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform quotas update")

        serializer = serializers.TenantQuotaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            backend = tenant.get_backend()
            backend.tenants.change_quota(**serializer.validated_data)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)

        return response.Response(
            {'status': 'Quota update was scheduled'}, status=status.HTTP_202_ACCEPTED)


class TemplateViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    lookup_field = 'uuid'


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'uuid'

    def perform_create(self, serializer):
        tenant = serializer.validated_data['tenant']
        backend = tenant.get_backend()

        if tenant.state != models.SharepointTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform user creation")

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
            new_password = serializer.validated_data.pop('password', None)
            if new_password and user.password != new_password:
                backend.users.change_password(id=user.backend_id, password=new_password)

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


class SiteViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    queryset = models.Site.objects.all()
    serializer_class = serializers.SiteSerializer
    lookup_field = 'uuid'

    def perform_create(self, serializer):
        user = serializer.validated_data['user']
        template = serializer.validated_data.pop('template')
        backend = user.tenant.get_backend()

        if user.tenant.state != models.SharepointTenant.States.OFFLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform user creation")

        try:
            backend_site = backend.sites.create(
                admin_id=user.admin_id,
                template_code=template.code,
                site_url=serializer.validated_data['site_url'],
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                warn_quota=serializer.validated_data.pop('warn_quota'),
                max_quota=serializer.validated_data.pop('max_quota'))

        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            site = serializer.save()
            site.site_url = backend_site.url
            site.save()

    def perform_destroy(self, site):
        backend = site.user.tenant.get_backend()
        try:
            backend.sites.delete(url=site.site_url)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            site.delete()
