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
            user_count=serializer.validated_data['user_count'])

    def get_serializer_class(self):
        serializer_class = super(TenantViewSet, self).get_serializer_class()
        if self.action == 'set_quotas':
            serializer_class = serializers.TenantQuotaSerializer
        return serializer_class

    @decorators.detail_route(methods=['post'])
    def set_quotas(self, request, **kwargs):
        if not request.user.is_staff:
            raise exceptions.PermissionDenied()

        tenant = self.get_object()
        if tenant.state != models.SharepointTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be in online to perform quotas update")

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        storage_size_quota = tenant.quotas.get(name=tenant.Quotas.storage_size)
        user_count_quota = tenant.quotas.get(name=tenant.Quotas.user_count)
        new_quotas_limits = {
            'storage_size': serializer.validated_data.get('storage_size', storage_size_quota.limit),
            'user_count': serializer.validated_data.get('user_count', user_count_quota.limit),
        }

        try:
            backend = tenant.get_backend()
            backend.tenants.change_quota(**new_quotas_limits)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)

        if 'storage_size' in serializer.validated_data:
            tenant.storage_size = serializer.validated_data['storage_size']
            tenant.save()
            tenant.set_quota_limit(tenant.Quotas.storage_size, tenant.storage_size)
        if 'user_count' in serializer.validated_data:
            tenant.user_count = serializer.validated_data['user_count']
            tenant.save()
            tenant.set_quota_limit(tenant.Quotas.user_count, tenant.user_count)

        return response.Response({'status': 'Quota was changed successfully'}, status=status.HTTP_200_OK)


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

        if user.tenant.state != models.SharepointTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform site creation")

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
