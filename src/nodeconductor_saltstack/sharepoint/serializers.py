from rest_framework import serializers

from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.models import SaltStackServiceProjectLink
from .models import Site


Sizes = (('small', 'Small'),
         ('medium', 'Medium'),
         ('large', 'Large'))


class SiteSerializer(structure_serializers.BaseResourceSerializer):
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
    storage_size = serializers.ChoiceField(write_only=True, choices=Sizes)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = Site
        view_name = 'sharepoint-sites-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'storage_size')
