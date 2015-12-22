from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink
from .models import ExchangeTenant, User


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

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = ExchangeTenant
        view_name = 'exchange-tenants-detail'
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'name', 'mailbox_size', 'max_users',
        )
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'mailbox_size', 'max_users',
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

            backend = ExchangeTenant(service_project_link=attrs['service_project_link']).get_backend()
            try:
                backend.tenants.check(tenant=attrs['name'], domain=attrs['domain'])
            except SaltStackBackendError as e:
                raise serializers.ValidationError({
                    'name': "This tenant name or domain is already taken: %s" % e.traceback_str})

        return attrs


class UserSerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = User
        view_name = 'exchange-users-detail'
        fields = (
            'url', 'uuid', 'tenant', 'tenant_uuid', 'tenant_domain', 'name',
            'first_name', 'last_name', 'username', 'password', 'mailbox_size',
        )
        read_only_fields = ('uuid', 'password')
        protected_fields = ('tenant',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'exchange-tenants-detail'},
        }
        related_paths = {
            'tenant': ('uuid', 'domain')
        }

    def validate(self, attrs):
        tenant = self.instance.tenant if self.instance else attrs['tenant']

        if attrs['mailbox_size'] > tenant.mailbox_size:
            raise serializers.ValidationError(
                {'mailbox_size': "Mailbox size should be lower than %s MB" % tenant.mailbox_size})

        user_count_quota = tenant.quotas.get(name='user_count')
        if user_count_quota.is_exceeded(delta=1):
            raise serializers.ValidationError('Tenant user count quota exceeded.')

        return attrs
