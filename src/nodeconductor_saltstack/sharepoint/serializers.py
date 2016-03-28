from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.quotas.serializers import BasicQuotaSerializer
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.models import SaltStackServiceProjectLink
from ..saltstack.serializers import PhoneValidationMixin
from .models import SharepointTenant, Template, User, SiteCollection


class SiteCollectionSerializer(serializers.HyperlinkedModelSerializer):

    storage = serializers.IntegerField(write_only=True, help_text='Site collection size limit, MB')

    template = serializers.HyperlinkedRelatedField(
        view_name='sharepoint-templates-detail',
        queryset=Template.objects.all(),
        lookup_field='uuid')
    template_code = serializers.ReadOnlyField(source='template.code')
    template_name = serializers.ReadOnlyField(source='template.name')
    quotas = BasicQuotaSerializer(many=True, read_only=True)

    class Meta(object):
        model = SiteCollection
        view_name = 'sharepoint-site-collections-detail'
        fields = ('url', 'uuid', 'template', 'template_code', 'template_name', 'user', 'storage', 'name', 'description',
                  'type', 'quotas', 'site_url', 'access_url', 'deletable')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'user': {'lookup_field': 'uuid', 'view_name': 'sharepoint-users-detail'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'sharepoint-tenants-detail'},
        }
        read_only_fields = ('uuid', 'access_url', 'type')
        protected_fields = ('template',)

    def validate_user(self, user):
        if user.tenant.state != SharepointTenant.States.ONLINE:
            raise serializers.ValidationError(
                'It is impossible to create site collection if user tenant is not online.')
        return user

    def validate(self, attrs):
        # TODO: Check that template belong to the same service settings.
        user = attrs['user']
        tenant = user.tenant
        storage_quota = tenant.quotas.get(name=tenant.Quotas.storage)
        if storage_quota.is_exceeded(delta=attrs['storage']):
            max_storage = storage_quota.limit - storage_quota.usage
            raise serializers.ValidationError(
                'Storage quota is over limit. Site collection cannot be greater then %s MB' % max_storage)

        if SiteCollection.objects.filter(name=attrs['name'], user__tenant=tenant).exists():
            raise serializers.ValidationError(
                'Site collection with name "%s" already exists in such tenant' % attrs['name'])

        return attrs


class UserSerializer(AugmentedSerializerMixin, PhoneValidationMixin, serializers.HyperlinkedModelSerializer):
    notify = serializers.BooleanField(write_only=True, required=False)

    personal_site_collection = SiteCollectionSerializer(read_only=True)

    class Meta(object):
        model = User
        view_name = 'sharepoint-users-detail'
        fields = (
            'url', 'uuid', 'tenant', 'tenant_uuid', 'tenant_domain', 'name', 'email',
            'first_name', 'last_name', 'username', 'password', 'phone', 'notify',
            'personal_site_collection',
        )
        read_only_fields = ('uuid', 'password')
        protected_fields = ('tenant', 'notify')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'sharepoint-tenants-detail'},
        }
        related_paths = {
            'tenant': ('uuid', 'domain')
        }

    def validate_tenant(self, tenant):
        if tenant.state != SharepointTenant.States.ONLINE:
            raise serializers.ValidationError('It is impossible to create site collection if tenant is not online.')
        storage_quota = tenant.quotas.get(name=SharepointTenant.Quotas.storage)
        if storage_quota.is_exceeded(delta=SiteCollection.Defaults.personal_site_collection['storage']):
            raise serializers.ValidationError('Tenant has not enough space for user creation.')
        return tenant

    def validate_name(self, name):
        if not self.instance:
            return name

        if self.instance.name == User.Defaults.admin['name'] and name != self.instance.name:
            raise serializers.ValidationError("Admin user's name cannot be changed.")

        return name

    def validate_username(self, username):
        if not self.instance:
            return username

        if self.instance.username == User.Defaults.admin['username'] and username != self.instance.username:
            raise serializers.ValidationError("Admin user's username cannot be changed.")

        return username


class TenantSerializer(PhoneValidationMixin, structure_serializers.PublishableResourceSerializer):
    MINIMUM_TENANT_STORAGE_SIZE = 1024

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='saltstack-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='saltstack-spl-detail',
        queryset=SaltStackServiceProjectLink.objects.all())

    storage = serializers.IntegerField(min_value=MINIMUM_TENANT_STORAGE_SIZE, write_only=True, initial=5 * 1024)
    site_name = serializers.CharField(help_text='Main site collection name.', write_only=True)
    site_description = serializers.CharField(help_text='Main site collection description.', write_only=True)
    template = serializers.HyperlinkedRelatedField(
        view_name='sharepoint-templates-detail',
        queryset=Template.objects.all(),
        lookup_field='uuid',
        write_only=True,
    )

    # IP of the Sharepoint management server. admin_url/site_url should be resolving to it.
    management_ip = serializers.SerializerMethodField()

    quotas = BasicQuotaSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)
    admin_site_collection = SiteCollectionSerializer(read_only=True)
    main_site_collection = SiteCollectionSerializer(read_only=True)
    phone = serializers.CharField(write_only=True, allow_blank=True, required=False)
    notify = serializers.BooleanField(write_only=True, required=False)

    def get_management_ip(self, tenant):
        return tenant.service_project_link.service.settings.options.get('sharepoint_management_ip', 'Unknown')

    def get_admin_site_collection_url(self, tenant):
        if tenant.admin_site_collection:
            return tenant.admin_site_collection.access_url
        return

    class Meta(structure_serializers.PublishableResourceSerializer.Meta):
        model = SharepointTenant
        view_name = 'sharepoint-tenants-detail'
        fields = structure_serializers.PublishableResourceSerializer.Meta.fields + (
            'domain', 'quotas', 'storage', 'management_ip', 'site_name', 'site_description', 'template',
            'admin', 'admin_site_collection', 'main_site_collection', 'phone', 'notify', 'access_url',
        )
        protected_fields = structure_serializers.PublishableResourceSerializer.Meta.protected_fields + (
            'domain', 'storage', 'site_name', 'site_description', 'template', 'phone', 'notify',
        )

    def validate(self, attrs):
        attrs = super(TenantSerializer, self).validate(attrs)

        if not self.instance:
            spl = attrs.get('service_project_link')

            sharepoint_tenant_number_quota = spl.quotas.get(name=spl.Quotas.sharepoint_tenant_number)
            if sharepoint_tenant_number_quota.is_exceeded(delta=1):
                raise serializers.ValidationError("You have reached the maximum number of allowed tenants.")

            spl_storage_quota = spl.quotas.get(name=spl.Quotas.sharepoint_storage)
            if spl_storage_quota.is_exceeded(delta=attrs.get('storage')):
                storage_left = spl_storage_quota.limit - spl_storage_quota.usage
                raise serializers.ValidationError({
                    'storage': ("Service project link quota exceeded: Total tenant storage size should be lower "
                                "than %s MB" % storage_left)
                })

            kwargs = dict(domain=attrs['domain'], service_project_link__service__settings=spl.service.settings)
            if SharepointTenant.objects.filter(**kwargs).exists():
                raise serializers.ValidationError({'domain': 'Tenant domain should be unique.'})

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

    notify = serializers.BooleanField(write_only=True, required=False)

    class Meta(object):
        model = User
        fields = ('password', 'notify')
        read_only_fields = ('password',)


# Should be initialized with tenant in context
class TenantQuotaSerializer(serializers.Serializer):
    storage = serializers.FloatField(
        min_value=TenantSerializer.MINIMUM_TENANT_STORAGE_SIZE, write_only=True, help_text='Maximum storage size, MB')

    def validate_storage(self, value):
        tenant = self.context['tenant']
        old_quota = tenant.quotas.get(name=SharepointTenant.Quotas.storage)
        if value < old_quota.usage:
            raise serializers.ValidationError('New storage quota limit cannot be lower than current usage.')

        diff = value - old_quota.limit
        if diff > 0:
            spl = tenant.service_project_link
            spl_storage_quota = spl.quotas.get(name=spl.Quotas.sharepoint_storage)
            if spl_storage_quota.is_exceeded(delta=diff):
                storage_left = spl_storage_quota.limit - spl_storage_quota.usage
                raise serializers.ValidationError(
                    "Service project link quota exceeded: Tenant size cannot be increased by more "
                    "than %s MB" % storage_left
                )
        return value


# Should be initialized with site_collection in context
class SiteCollectionQuotaSerializer(serializers.Serializer):
    storage = serializers.FloatField(min_value=1, write_only=True, help_text='Maximum storage size, MB')

    def validate(self, attrs):
        site_collection = self.context['site_collection']
        site_collection_quota = site_collection.quotas.get(name=SiteCollection.Quotas.storage)

        old_limit = site_collection_quota.limit
        new_limit = attrs['storage']
        storage_quota = site_collection.user.tenant.quotas.get(name=SharepointTenant.Quotas.storage)
        if new_limit > old_limit and storage_quota.is_exceeded(delta=new_limit-old_limit):
            max_storage = storage_quota.limit - storage_quota.usage + old_limit
            raise serializers.ValidationError(
                'Storage quota is over limit. Site collection cannot be greater then %s MB' % max_storage)

        current_usage = site_collection_quota.usage
        if new_limit < current_usage:
            raise serializers.ValidationError('New limit cannot be lower than current usage.')

        return attrs
