import binascii

from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.quotas.serializers import QuotaSerializer
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink
from . import models


class ExchangeDomainSerializer(serializers.ModelSerializer):

    class Meta():
        model = models.ExchangeTenant
        fields = ('domain',)


class TenantSerializer(structure_serializers.BaseResourceSerializer):
    MAX_TENANT_SIZE = 2 * 1024 * 1024  # 2TB

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='saltstack-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='saltstack-spl-detail',
        queryset=SaltStackServiceProjectLink.objects.all(),
        write_only=True)

    quotas = QuotaSerializer(many=True, read_only=True)

    # Link to Outlook Web Access
    owa_url = serializers.SerializerMethodField()

    # Link to Exchange Control Panel
    ecp_url = serializers.SerializerMethodField()

    def get_owa_url(self, tenant):
        return tenant.service_project_link.service.settings.options.get('owa_url', 'Unknown')

    def get_ecp_url(self, tenant):
        return tenant.service_project_link.service.settings.options.get('ecp_url', 'Unknown')

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.ExchangeTenant
        view_name = 'exchange-tenants-detail'
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'mailbox_size', 'max_users', 'domain',
        )
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'mailbox_size', 'max_users', 'quotas', 'owa_url', 'ecp_url',
        )

    def validate(self, attrs):
        if not self.instance:
            spl = attrs['service_project_link']

            tenant_size = int(attrs['mailbox_size']) * int(attrs['max_users'])
            if tenant_size * .9 > self.MAX_TENANT_SIZE:
                raise serializers.ValidationError({
                    'max_users': "Total mailbox size should be lower than 2 TB"})

            exchange_storage_quota = spl.quotas.get(name='exchange_storage')
            if exchange_storage_quota.is_exceeded(delta=tenant_size):
                storage_left = exchange_storage_quota.limit - exchange_storage_quota.usage
                raise serializers.ValidationError({
                    'max_users': "Total mailbox size should be lower than %s MB" % storage_left})

            attrs['backend_id'] = 'NC_%X' % (binascii.crc32(attrs['domain']) % (1 << 32))

            backend = models.ExchangeTenant(service_project_link=spl).get_backend()
            try:
                backend.tenants.check(tenant=attrs['backend_id'], domain=attrs['domain'])
            except SaltStackBackendError as e:
                raise serializers.ValidationError({
                    'name': "This tenant name or domain is already taken: %s" % e.traceback_str})

        return attrs


class BasePropertySerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = NotImplemented
        view_name = NotImplemented
        fields = 'url', 'uuid', 'tenant', 'tenant_uuid', 'tenant_domain',
        read_only_fields = 'uuid',
        protected_fields = 'tenant',
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'exchange-tenants-detail'},
        }
        related_paths = {
            'tenant': ('uuid', 'domain')
        }


class UserPasswordSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.User
        fields = ('password',)


class UserSerializer(BasePropertySerializer):

    class Meta(BasePropertySerializer.Meta):
        model = models.User
        view_name = 'exchange-users-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'name', 'first_name', 'last_name', 'username', 'password', 'mailbox_size',
            'office', 'phone', 'department', 'company', 'title', 'manager',
        )
        # password update is handled separately in views.py
        read_only_fields = BasePropertySerializer.Meta.read_only_fields + ('password',)
        extra_kwargs = dict(
            manager={'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            **BasePropertySerializer.Meta.extra_kwargs
        )

    def validate_name(self, value):
        if models.User.objects.filter(name=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError('This field must be unique.')
        return value

    def validate(self, attrs):
        tenant = self.instance.tenant if self.instance else attrs['tenant']

        # validation for user creation
        if not self.instance:
            if attrs['mailbox_size'] > tenant.mailbox_size:
                raise serializers.ValidationError(
                    {'mailbox_size': "Mailbox size should be lower than %s MB" % tenant.mailbox_size})

            user_count_quota = tenant.quotas.get(name='user_count')
            if user_count_quota.is_exceeded(delta=1):
                raise serializers.ValidationError('Tenant user count quota exceeded.')

        return attrs


class ContactSerializer(BasePropertySerializer):

    class Meta(BasePropertySerializer.Meta):
        model = models.Contact
        view_name = 'exchange-contacts-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'name', 'email', 'first_name', 'last_name',
        )


class GroupMemberSerializer(serializers.Serializer):

    users = serializers.HyperlinkedRelatedField(
        queryset=models.User.objects.all(),
        view_name='exchange-users-detail',
        lookup_field='uuid',
        write_only=True,
        many=True)


class GroupSerializer(BasePropertySerializer):

    class Meta(BasePropertySerializer.Meta):
        model = models.Group
        view_name = 'exchange-groups-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'manager', 'manager_uuid', 'manager_name', 'name', 'username',
        )
        extra_kwargs = dict(
            BasePropertySerializer.Meta.extra_kwargs.items() +
            {'manager': {'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'}}.items()
        )
        related_paths = dict(
            BasePropertySerializer.Meta.related_paths.items() +
            {'manager': ('uuid', 'name')}.items()
        )
