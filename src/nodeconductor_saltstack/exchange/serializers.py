from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink
from .models import ExchangeTenant


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
            'name', 'domain',
        )
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'mailbox_size', 'max_users',
        )

    def validate(self, attrs):
        spl = attrs.get('service_project_link') or self.instance.service_project_link
        mailbox_size = attrs.get('mailbox_size') or self.instance.mailbox_size
        max_users = attrs.get('max_users') or self.instance.max_users

        tenant_size = int(mailbox_size) * int(max_users)
        if tenant_size * .9 > self.MAX_TENANT_SIZE:
            raise serializers.ValidationError({
                'max_users': "Total mailbox size should be lower than 2 TB"})

        exchange_storage_quota = spl.quotas.get(name='exchange_storage')
        if exchange_storage_quota.is_exceeded(delta=tenant_size):
            storage_left = exchange_storage_quota.limit - exchange_storage_quota.usage
            raise serializers.ValidationError({
                'max_users': "Total mailbox size should be lower than %s MB" % storage_left})

        backend = ExchangeTenant(service_project_link=spl).get_backend()
        name = attrs.get('name') or self.instance.name
        domain = attrs.get('domain') or self.instance.domain
        try:
            backend.tenants.check(tenant=name, domain=domain)
        except SaltStackBackendError as e:
            raise serializers.ValidationError({
                'name': "This tenant name or domain is already taken: %s" % e.traceback_str})

        return attrs


class PropertySerializer(serializers.Serializer):

    def get_url(self, obj):
        resource = self.context['resource']
        request = self.context['request']
        return reverse(
            self.get_url_name(),
            kwargs={'tenant_uuid': resource.uuid.hex, 'pk': obj.id}, request=request)


class UserSerializer(PropertySerializer):
    url = serializers.SerializerMethodField()
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.SlugField(write_only=True)
    first_name = serializers.CharField(max_length=60)
    last_name = serializers.CharField(max_length=60)
    mailbox_size = serializers.IntegerField(write_only=True)
    password = serializers.EmailField(read_only=True)

    def get_url_name(self):
        return 'exchange-users-detail'

    def validate_mailbox_size(self, value):
        tenant = self.context['resource']
        max_size = tenant.mailbox_size
        if value and value > max_size:
            raise serializers.ValidationError("Mailbox size should be lower than %s MB" % max_size)
        return value

    def validate(self, attrs):
        tenant = self.context['resource']
        user_count_quota = tenant.quotas.get(name='user_count')
        if user_count_quota.is_exceeded(delta=1):
            raise serializers.ValidationError('Tenant user count quota exceeded.')
        return attrs


class ContactSerializer(PropertySerializer):
    url = serializers.SerializerMethodField()
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    name = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(max_length=60, write_only=True)
    last_name = serializers.CharField(max_length=60, write_only=True)

    def get_url_name(self):
        return 'exchange-contacts-detail'


class GroupMemberSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class GroupSerializer(PropertySerializer):
    url = serializers.SerializerMethodField()
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField(read_only=True)
    username = serializers.SlugField(write_only=True)
    manager_email = serializers.EmailField(write_only=True)
    members = serializers.SerializerMethodField(read_only=True)

    def get_url_name(self):
        return 'exchange-groups-detail'

    def get_members(self, obj):
        backend = self.context['resource'].get_backend()
        return [GroupMemberSerializer(member).data for member in backend.groups.list_members(id=obj.id)]

    def validate_manager_email(self, value):
        if value:
            backend = self.context['resource'].get_backend()
            try:
                next(backend.users.findall(email=value))
            except StopIteration:
                raise serializers.ValidationError("Unknown tenant user: %s" % value)
        return value
