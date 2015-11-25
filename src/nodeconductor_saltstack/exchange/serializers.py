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

    max_users = serializers.IntegerField(write_only=True)
    mailbox_size = serializers.IntegerField(write_only=True)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = Tenant
        view_name = 'saltstack-tenants-detail'
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'name', 'domain',
        )
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'max_users', 'mailbox_size',
        )


class TenantUserSerializer(serializers.Serializer):

    url = serializers.SerializerMethodField()
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=60)
    last_name = serializers.CharField(max_length=60)
    mailbox_size = serializers.IntegerField()

    def get_url(self, obj):
        domain = self.context['domain']
        request = self.context['request']
        return reverse(
            'saltstack-tenantusers-detail',
            kwargs={'domain_uuid': domain.uuid.hex, 'pk': obj.id}, request=request)
