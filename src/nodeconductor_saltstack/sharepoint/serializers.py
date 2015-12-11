from rest_framework import serializers

from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.models import SaltStackServiceProjectLink
from .models import SharepointTenant, Template


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
