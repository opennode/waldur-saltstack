from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeconductor.structure import serializers as structure_serializers
from . import models


Sizes = (('small', 'Small'),
         ('medium', 'Medium'),
         ('large', 'Large'))


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'backend_url': 'URL for SaltStack master API (required, e.g.: http://salt-master.example.com:8080)',
        'username': 'PAM user account with access to SaltStack API',
        'password': '',
    }

    SERVICE_ACCOUNT_EXTRA_FIELDS = {
        'exchange_target': 'Salt minion target with MS Exchange Domains',
        'sharepoint_target': 'Salt minion target with MS Sharepoint Sites',
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.SaltStackService
        view_name = 'saltstack-detail'


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.SaltStackServiceProjectLink
        view_name = 'saltstack-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'saltstack-detail'},
        }


class DomainSerializer(structure_serializers.BaseResourceSerializer):
    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='saltstack-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='saltstack-spl-detail',
        queryset=models.SaltStackServiceProjectLink.objects.all(),
        write_only=True)

    domain = serializers.CharField(write_only=True, max_length=255)
    bucket_size = serializers.ChoiceField(write_only=True, choices=Sizes)
    mailbox_size = serializers.IntegerField(write_only=True)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Domain
        view_name = 'saltstack-domains-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'bucket_size', 'mailbox_size')


class SiteSerializer(structure_serializers.BaseResourceSerializer):
    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='saltstack-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='saltstack-spl-detail',
        queryset=models.SaltStackServiceProjectLink.objects.all(),
        write_only=True)

    domain = serializers.CharField(write_only=True, max_length=255)
    storage_size = serializers.ChoiceField(write_only=True, choices=Sizes)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Site
        view_name = 'saltstack-sites-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'storage_size')


class DomainUserSerializer(serializers.Serializer):

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
            'saltstack-domainusers-detail',
            kwargs={'domain_uuid': domain.uuid.hex, 'pk': obj.id}, request=request)
