from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.models import SaltStackServiceProjectLink
from .models import SharepointTenant, Template, User


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

    domain = serializers.CharField(write_only=True, max_length=255)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = SharepointTenant
        view_name = 'sharepoint-tenants-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + ('domain',)


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
            'url', 'uuid', 'name', 'email', 'tenant',
            'username', 'first_name', 'last_name',
            'admin_id', 'password',
        )
        read_only_fields = ('name', 'email', 'uuid', 'admin_id', 'password')
        write_only_fields = ('username', 'first_name', 'last_name')
        protected_fields = ('tenant',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'sharepoint-tenants-detail'},
        }
        related_paths = {
            'tenant': ('uuid', 'domain')
        }
