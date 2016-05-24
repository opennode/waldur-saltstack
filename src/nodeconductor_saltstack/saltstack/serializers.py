import re

from rest_framework import serializers
from nodeconductor.quotas import serializers as quotas_serializers
from nodeconductor.structure import serializers as structure_serializers

from . import models


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'backend_url': 'URL for SaltStack master API (required, e.g.: http://salt-master.example.com:8080)',
        'username': 'PAM user account with access to SaltStack API',
        'password': '',
    }

    SERVICE_ACCOUNT_EXTRA_FIELDS = {
        # Exchange
        'exchange_target': 'Salt minion target with MS Exchange Domains',
        'sms_email_from': 'Sender e-mail address for SMS notifications',
        'sms_email_rcpt': 'Recipient e-mail template for SMS notifications (e.g. "{phone}@example.com")',
        'phone_regex': 'Phone number validation regex',
        'owa_url': 'URL for Outlook Web Access',
        'ecp_url': 'Exchange Control Panel',
        # Sharepoint
        'sharepoint_target': 'Salt minion target with MS Sharepoint Sites',
        'sharepoint_management_ip': 'IP of the Sharepoint server. Used for setting up host resolution.'
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.SaltStackService
        view_name = 'saltstack-detail'


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):
    quotas = quotas_serializers.QuotaSerializer(many=True, read_only=True)

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.SaltStackServiceProjectLink
        view_name = 'saltstack-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'saltstack-detail'},
        }
        fields = structure_serializers.BaseServiceProjectLinkSerializer.Meta.fields + ('quotas',)


class PhoneValidationMixin(object):

    def validate(self, attrs):
        attrs = super(PhoneValidationMixin, self).validate(attrs)
        # XXX: This code is fragile and tricky we need at to separate phone validator for different serializers.
        if self.instance:
            try:
                tenant = self.instance.tenant
            except AttributeError:
                tenant = self.instance
        else:
            tenant = attrs.get('tenant')

        phone = attrs.get('phone')
        spl = tenant.service_project_link if tenant is not None else attrs['service_project_link']
        if phone:
            options = spl.service.settings.options or {}
            phone_regex = options.get('phone_regex')
            if phone_regex and not re.search(phone_regex, phone):
                raise serializers.ValidationError({'phone': "Invalid phone number."})

        if attrs.get('notify', False) and not phone:
            raise serializers.ValidationError({'phone': "Missed phone number for notification."})

        return attrs
