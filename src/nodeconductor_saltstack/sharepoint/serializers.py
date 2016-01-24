from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.quotas.serializers import QuotaSerializer
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink
from .models import SharepointTenant, Template, User, Site


class TenantSerializer(structure_serializers.BaseResourceSerializer):
    description = serializers.CharField(allow_blank=False)

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='saltstack-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='saltstack-spl-detail',
        queryset=SaltStackServiceProjectLink.objects.all(),
        write_only=True)

    template = serializers.HyperlinkedRelatedField(
        view_name='sharepoint-templates-detail',
        queryset=Template.objects.all(),
        write_only=True,
        lookup_field='uuid')

    storage_size = serializers.IntegerField(write_only=True)
    users_count = serializers.IntegerField(min_value=1, write_only=True, help_text='Maximum users count')

    # IP of the Sharepoint management server. admin_url/site_url should be resolving to it.
    management_ip = serializers.SerializerMethodField()
    quotas = QuotaSerializer(many=True, read_only=True)

    def get_management_ip(self, tenant):
        return tenant.service_project_link.service.settings.options.get('sharepoint_management_ip', 'Unknown')

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = SharepointTenant
        view_name = 'sharepoint-tenants-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'template', 'domain', 'site_name', 'site_url',
            'admin_url', 'admin_login', 'admin_password',
            'storage_size', 'users_count', 'management_ip',
            'quotas',
        )
        read_only_fields = structure_serializers.BaseResourceSerializer.Meta.read_only_fields + (
            'site_url', 'admin_url', 'admin_login', 'admin_password', 'quotas',
        )
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'template', 'name', 'description', 'domain', 'site_name', 'storage_size'
        )

    def validate(self, attrs):
        spl = attrs.get('service_project_link')
        if spl.service.settings != attrs['template'].settings:
            raise serializers.ValidationError({
                'template': "Template must be within the same service settings"})

        sharepoint_tenant_number_quota = spl.quotas.get(name=spl.Quotas.sharepoint_tenant_number)
        if sharepoint_tenant_number_quota.is_exceeded(delta=1):
            raise serializers.ValidationError("You have reached the maximum number of allowed tenants.")

        sharepoint_storage_quota = spl.quotas.get(name=spl.Quotas.sharepoint_storage)
        if sharepoint_storage_quota.is_exceeded(delta=int(attrs['storage_size'])):
            storage_left = sharepoint_storage_quota.limit - sharepoint_storage_quota.usage
            raise serializers.ValidationError({
                'storage_size': "Total tenant size should be lower than %s MB" % storage_left})

        backend = SharepointTenant(service_project_link=spl).get_backend()
        try:
            backend.tenants.check(tenant=attrs['name'], domain=attrs['domain'])
        except SaltStackBackendError as e:
            raise serializers.ValidationError({
                'name': "This tenant name is already taken: %s" % e.traceback_str})

        return attrs


class TenantQuotaSerializer(serializers.Serializer):
    storage_size = serializers.FloatField(
        min_value=1, write_only=True, help_text='Maximum storage size, MB', required=False)
    users_count = serializers.IntegerField(
        min_value=1, write_only=True, help_text='Maximum users count', required=False)


class TemplateSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = Template
        view_name = 'sharepoint-templates-detail'
        fields = ('url', 'uuid', 'name', 'code')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class UserSerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = User
        view_name = 'sharepoint-users-detail'
        fields = (
            'url', 'uuid', 'tenant', 'tenant_uuid', 'tenant_domain', 'name', 'email',
            'first_name', 'last_name', 'username', 'password',
        )
        read_only_fields = ('uuid',)
        protected_fields = ('tenant',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'sharepoint-tenants-detail'},
        }
        related_paths = {
            'tenant': ('uuid', 'domain')
        }

    def get_fields(self):
        fields = super(UserSerializer, self).get_fields()
        try:
            method = self.context['view'].request.method
        except (KeyError, AttributeError):
            pass
        else:
            if method == 'POST':
                # disabple password field during creation
                fields['password'].read_only = True

        return fields

    def validate(self, attrs):
        if not self.instance:
            tenant = attrs['tenant']
            user_count_quota = tenant.quotas.get(name=tenant.Quotas.user_count)
            if user_count_quota.is_exceeded(delta=1):
                raise serializers.ValidationError('Cannot add new users to tenant. Its user_count quota is over limit.')
        return attrs


class SiteSerializer(serializers.HyperlinkedModelSerializer):

    template = serializers.HyperlinkedRelatedField(
        view_name='sharepoint-templates-detail',
        queryset=Template.objects.all(),
        write_only=True,
        lookup_field='uuid')

    max_quota = serializers.IntegerField(write_only=True, help_text='Maximum site quota, GB')
    warn_quota = serializers.IntegerField(write_only=True, help_text='Warning site quota, GB')

    class Meta(object):
        model = Site
        view_name = 'sharepoint-sites-detail'
        fields = (
            'url', 'uuid', 'template', 'user',
            'site_url', 'name', 'description',
            'max_quota', 'warn_quota',
        )
        read_only_fields = ('uuid',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'user': {'lookup_field': 'uuid', 'view_name': 'sharepoint-users-detail'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'sharepoint-tenants-detail'},
        }

    def validate(self, attrs):
        if attrs['warn_quota'] > attrs['max_quota']:
            raise serializers.ValidationError({
                'warn_quota': "Warning quota exceeds maximum quota"})
        return attrs
