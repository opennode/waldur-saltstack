from rest_framework import decorators, exceptions, mixins, response, viewsets
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT

from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure import views as structure_views
from nodeconductor_saltstack.saltstack.views import track_exceptions

from . import models, serializers, filters
from ..saltstack.backend import SaltStackBackendError
from ..saltstack.views import BasePropertyViewSet
from ..saltstack.utils import sms_user_password
from log import event_logger


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

        old_quota = tenant.quotas.get(name=models.SharepointTenant.Quotas.storage)
        new_quota_limit = serializer.validated_data['storage']
        tenant.set_quota_limit(models.SharepointTenant.Quotas.storage, new_quota_limit)

        event_logger.sharepoint_tenant.info(
            'Sharepoint tenant {tenant_name} quota has been updated from %s to %s.' % (old_quota.limit, new_quota_limit),
            event_type='sharepoint_tenant_quota_update',
            event_context={
                'tenant': tenant,
            })
        return response.Response({'status': 'Quotas were successfully changed.'}, status=HTTP_200_OK)


class TemplateViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    lookup_field = 'uuid'


class UserViewSet(BasePropertyViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_class = filters.UserFilter
    backend_name = 'users'

    def pre_create(self, serializer):
        self.notify = serializer.validated_data.pop('notify', False)

    def post_create(self, user, serializer, backend_user):
        user.admin_id = backend_user.admin_id
        user.password = backend_user.password
        user.save()
        user.init_personal_site_collection(backend_user.personal_site_collection_url)

        if self.notify:
            sms_user_password(user)

    # XXX: put was added as portal has a temporary bug with widget update
    @decorators.detail_route(methods=['post', 'put'])
    @track_exceptions
    def password(self, request, pk=None, **kwargs):
        user = self.get_object()
        backend = self.get_backend(user.tenant)
        reset_response = backend.reset_password(id=user.backend_id)
        user.password = reset_response.password
        user.save()

        serializer_class = serializers.UserPasswordSerializer
        serializer = serializer_class(instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('notify'):
            sms_user_password(user)

        event_logger.sharepoint_user.info(
            'Sharepoint user {affected_user_name} ({affected_user_email}) password has been reset.',
            event_type='sharepoint_user_password_reset',
            event_context={
                'affected_user': user,
            })

        return response.Response(serializer.data, status=HTTP_200_OK)


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
        tenant = site_collection.user.tenant
        backend = tenant.get_backend()

        serializer = serializers.SiteCollectionQuotaSerializer(
            data=request.data, context={'site_collection': site_collection})
        serializer.is_valid(raise_exception=True)

        # If personal site collection was not initialized - check if it exists
        # XXX: identification via template is not logical. Need to handle backend_id for site collections.
        if site_collection.type == models.SiteCollection.Types.PERSONAL and site_collection.template is None:
            try:
                check_result = backend.site_collections.check(url=site_collection.access_url)
            except SaltStackBackendError:
                return response.Response(
                    {'detail': 'User personal site collection is not initialized'}, status=HTTP_409_CONFLICT)
            else:
                site_collection.template = models.Template.objects.filter(
                    code=check_result.template_code, settings=tenant.service_project_link.service.settings).first()
                site_collection.save()

        storage = serializer.validated_data['storage']
        old_quota = site_collection.quotas.get(name=models.SiteCollection.Quotas.storage)
        backend.site_collections.set_storage(url=site_collection.access_url, storage=storage)
        site_collection.set_quota_limit(models.SiteCollection.Quotas.storage, storage)

        event_logger.sharepoint_site_collection.info(
            ('Sharepoint site collection {site_collection_name} quota has been updated from %s to %s.'
             % (old_quota.limit, storage)),
            event_type='sharepoint_site_collection_quota_update',
            event_context={
                'site_collection': site_collection,
            })

        return response.Response({'status': 'Storage quota was successfully changed.'}, status=HTTP_200_OK)
