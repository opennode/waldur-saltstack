from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.models import SaltStackServiceProjectLink
from .models import Tenant


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

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = Tenant
        view_name = 'exchange-tenants-detail'
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'name', 'domain',
        )
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'mailbox_size', 'max_users',
        )

    def validate(self, attrs):
        spl = attrs['service_project_link']
        qs = Tenant.objects.filter(
            service_project_link__service=spl.service,
            state=Tenant.States.ONLINE)

        if qs.filter(name=attrs['name']).exists():
            raise serializers.ValidationError({'name': "This name is already used"})

        if qs.filter(domain=attrs['domain']).exists():
            raise serializers.ValidationError({'domain': "This domain is already used"})

        tenant_size = int(attrs['mailbox_size']) * int(attrs['max_users'])
        if tenant_size * .9 > 2048:
            raise serializers.ValidationError({
                'max_users': "Total mailbox size should be lower than 2 TB"})

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
        max_size = self.context['resource'].mailbox_size
        if value and value > max_size:
            raise serializers.ValidationError("Mailbox size should be lower than %s GB" % max_size)
        return value

    def validate(self, attrs):
        tenant = self.context['resource']
        users = tenant.get_backend().users.list()

        if users and "{first_name} {last_name}".format(**attrs) in (u.name for u in users):
            raise serializers.ValidationError({'first_name': "This name is already used"})

        return attrs


class ContactSerializer(PropertySerializer):
    id = serializers.CharField(read_only=True)

    def get_url_name(self):
        return 'exchange-contacts-detail'


class GroupSerializer(PropertySerializer):
    id = serializers.CharField(read_only=True)

    def get_url_name(self):
        return 'exchange-groups-detail'
