from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.quotas.serializers import QuotaSerializer
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.models import SaltStackServiceProjectLink
from .models import SharepointTenant, Template, User, SiteCollection


class TenantSerializer(structure_serializers.BaseResourceSerializer):
    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='saltstack-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='saltstack-spl-detail',
        queryset=SaltStackServiceProjectLink.objects.all(),
        write_only=True)

    user_count = serializers.IntegerField(min_value=1, write_only=True, initial=10)
    storage = serializers.IntegerField(min_value=1, write_only=True, initial=5*1024)

    # IP of the Sharepoint management server. admin_url/site_url should be resolving to it.
    management_ip = serializers.SerializerMethodField()
    quotas = QuotaSerializer(many=True, read_only=True)
    admin_url = serializers.SerializerMethodField()

    def get_management_ip(self, tenant):
        return tenant.service_project_link.service.settings.options.get('sharepoint_management_ip', 'Unknown')

    def get_admin_url(self, tenant):
        if tenant.admin_site_collection:
            return tenant.admin_site_collection.access_url
        return

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = SharepointTenant
        view_name = 'sharepoint-tenants-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'quotas', 'user_count', 'storage', 'initialization_status', 'admin_url', 'management_ip',
        )
        read_only_fields = structure_serializers.BaseResourceSerializer.Meta.read_only_fields + (
            'initialization_status',
        )
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'domain', 'user_count', 'storage',
        )

    def validate(self, attrs):
        if not self.instance:
            spl = attrs.get('service_project_link')

            sharepoint_tenant_number_quota = spl.quotas.get(name=spl.Quotas.sharepoint_tenant_number)
            if sharepoint_tenant_number_quota.is_exceeded(delta=1):
                raise serializers.ValidationError("You have reached the maximum number of allowed tenants.")

            sharepoint_storage_quota = spl.quotas.get(name=spl.Quotas.sharepoint_storage)
            if sharepoint_storage_quota.is_exceeded(delta=attrs.get('storage')):
                storage_left = sharepoint_storage_quota.limit - sharepoint_storage_quota.usage
                raise serializers.ValidationError({
                    'storage': "Total tenant size should be lower than %s MB" % storage_left})

            users_storage = attrs['user_count'] * SiteCollection.Defaults.personal_site_collection['storage']
            admin_storage = SiteCollection.Defaults.admin_site_collection['storage']

            if users_storage + admin_storage > attrs['storage']:
                raise serializers.ValidationError(
                    'Tenant size should be bigger then %s MB, if it needs to support %s users.' %
                    (users_storage + admin_storage, attrs['user_count'])
                )

        return attrs


class TemplateSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = Template
        view_name = 'sharepoint-templates-detail'
        fields = ('url', 'uuid', 'name', 'code')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class UserPasswordSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = User
        fields = ('password',)


class UserSerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = User
        view_name = 'sharepoint-users-detail'
        fields = (
            'url', 'uuid', 'tenant', 'tenant_uuid', 'tenant_domain', 'name', 'email',
            'first_name', 'last_name', 'username', 'password',
        )
        read_only_fields = ('uuid', 'password')
        protected_fields = ('tenant',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'sharepoint-tenants-detail'},
        }
        related_paths = {
            'tenant': ('uuid', 'domain')
        }

    def validate(self, attrs):
        if not self.instance:
            tenant = attrs['tenant']
            user_count_quota = tenant.quotas.get(name=tenant.Quotas.user_count)
            if user_count_quota.is_exceeded(delta=1):
                raise serializers.ValidationError('Cannot add new users to tenant. Its user_count quota is over limit.')
        return attrs


class MainSiteCollectionSerializer(serializers.HyperlinkedModelSerializer):

    template = serializers.HyperlinkedRelatedField(
        view_name='sharepoint-templates-detail',
        queryset=Template.objects.all(),
        lookup_field='uuid')

    storage = serializers.IntegerField(write_only=True, help_text='Main site collection size limit, MB')
    template_code = serializers.ReadOnlyField(source='template.code')
    template_name = serializers.ReadOnlyField(source='template.name')

    class Meta(object):
        model = SiteCollection
        view_name = 'sharepoint-site-collections-detail'
        fields = (
            'url', 'uuid', 'template', 'template_code', 'template_name', 'user', 'storage', 'name', 'description',
        )
        read_only_fields = ('uuid',)
        protected_fields = ('template',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'user': {'lookup_field': 'uuid', 'view_name': 'sharepoint-users-detail'},
        }

    def validate(self, attrs):
        user = attrs['user']
        tenant = user.tenant
        storage_quota = tenant.quotas.get(name=tenant.Quotas.storage)
        # With main site collection we also creating admin and personal collections - we need to count their quotas too.
        main_site_collection_storage = attrs['storage']
        admin_site_collection_storage = SiteCollection.Defaults.admin_site_collection['storage']
        user_count = tenant.quotas.get(name=tenant.Quotas.user_count).limit
        personal_site_collection_storage = SiteCollection.Defaults.presonal_site_collection['storage'] * user_count
        storage = main_site_collection_storage + admin_site_collection_storage + personal_site_collection_storage
        if storage_quota.is_exceeded(delta=storage):
            max_storage = (storage_quota.limit - storage_quota.usage -
                           admin_site_collection_storage - personal_site_collection_storage)
            raise serializers.ValidationError(
                'Storage quota is over limit. Site collection cannot be greater then %s MB.' % max_storage)
        return attrs

    # TODO: Check that template belong to the same service settings.


class SiteCollectionSerializer(MainSiteCollectionSerializer):

    storage = serializers.IntegerField(write_only=True, help_text='Site collection size limit, MB')

    quotas = QuotaSerializer(many=True, read_only=True)

    class Meta(MainSiteCollectionSerializer.Meta):
        fields = MainSiteCollectionSerializer.Meta.fields + ('quotas', 'site_url', 'access_url')
        extra_kwargs = dict(
            tenant={'lookup_field': 'uuid', 'view_name': 'sharepoint-tenants-detail'},
            **MainSiteCollectionSerializer.Meta.extra_kwargs
        )
        read_only_fields = MainSiteCollectionSerializer.Meta.read_only_fields + ('access_url',)

    def validate(self, attrs):
        user = attrs['user']
        tenant = user.tenant
        storage_quota = tenant.quotas.get(name=tenant.Quotas.storage)
        if storage_quota.is_exceeded(delta=attrs['storage']):
            max_storage = storage_quota.limit - storage_quota.usage
            raise serializers.ValidationError(
                'Storage quota is over limit. Site collection cannot be greater then %s MB' % max_storage)
        return attrs


# Should be initialized with site_collection in context
class SiteCollectionQuotaSerializer(serializers.Serializer):
    storage = serializers.FloatField(min_value=1, write_only=True, help_text='Maximum storage size, MB')

    def validate(self, attrs):
        site_collection = self.context['site_collection']
        old_storage = site_collection.quotas.get(name=SiteCollection.Quotas.storage).limit
        new_storage = attrs['storage']
        storage_quota = site_collection.user.tenant.quotas.get(name=SharepointTenant.Quotas.storage)
        if new_storage > old_storage and storage_quota.is_exceeded(delta=new_storage-old_storage):
            max_storage = storage_quota.limit - storage_quota.usage + old_storage
            raise serializers.ValidationError(
                'Storage quota is over limit. Site collection cannot be greater then %s MB' % max_storage)
        return attrs
