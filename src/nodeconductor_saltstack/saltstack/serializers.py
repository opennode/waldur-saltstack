from nodeconductor.structure import serializers as structure_serializers
from . import models


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
