import os
import re
import binascii

from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.quotas.exceptions import QuotaExceededException
from nodeconductor.quotas.serializers import QuotaSerializer
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink
from . import models


class ExchangeDomainSerializer(serializers.ModelSerializer):

    class Meta():
        model = models.ExchangeTenant
        fields = ('domain',)


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

    quotas = QuotaSerializer(many=True, read_only=True)

    # Link to Outlook Web Access
    owa_url = serializers.SerializerMethodField()

    # Link to Exchange Control Panel
    ecp_url = serializers.SerializerMethodField()

    def get_owa_url(self, tenant):
        return tenant.service_project_link.service.settings.options.get('owa_url', 'Unknown')

    def get_ecp_url(self, tenant):
        return tenant.service_project_link.service.settings.options.get('ecp_url', 'Unknown')

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.ExchangeTenant
        view_name = 'exchange-tenants-detail'
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'mailbox_size', 'max_users', 'domain',
        )
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'domain', 'mailbox_size', 'max_users', 'quotas', 'owa_url', 'ecp_url',
        )

    def validate(self, attrs):
        if not self.instance:
            spl = attrs['service_project_link']

            tenant_size = int(attrs['mailbox_size']) * int(attrs['max_users'])
            if tenant_size * .9 > self.MAX_TENANT_SIZE:
                raise serializers.ValidationError({
                    'max_users': "Total mailbox size should be lower than 2 TB"})

            spl_storage_quota = spl.quotas.get(name=spl.Quotas.exchange_storage)
            if spl_storage_quota.is_exceeded(delta=tenant_size):
                storage_left = spl_storage_quota.limit - spl_storage_quota.usage
                raise serializers.ValidationError({
                    'max_users': ("Service project link quota exceeded: Total mailbox size should be lower than %s MB"
                                  % storage_left)
                })

            service_settings_storage_quota = spl.service.settings.quotas.get(
                name=spl.service.settings.Quotas.exchange_storage)
            if service_settings_storage_quota.is_exceeded(delta=tenant_size):
                storage_left = service_settings_storage_quota.limit - service_settings_storage_quota.usage
                raise serializers.ValidationError({
                    'max_users': "Service quota exceeded: Total mailbox size should be lower than %s MB" % storage_left})

            # generate a random name to be used as unique tenant id in MS Exchange
            # Example of formt: NC_28052BF28A
            attrs['backend_id'] = 'NC_%s' % binascii.b2a_hex(os.urandom(5)).upper()

            backend = models.ExchangeTenant(service_project_link=spl).get_backend()
            try:
                backend.tenants.check(tenant=attrs['backend_id'], domain=attrs['domain'])
            except SaltStackBackendError as e:
                raise serializers.ValidationError({
                    'name': "This tenant name or domain is already taken: %s" % e.traceback_str})

        return attrs

    def get_fields(self):
        fields = super(TenantSerializer, self).get_fields()

        try:
            request = self.context['view'].request
            user = request.user
        except (KeyError, AttributeError):
            return fields

        if not user.is_staff:
            del fields['ecp_url']

        return fields


class BasePropertySerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = NotImplemented
        view_name = NotImplemented
        fields = 'url', 'uuid', 'tenant', 'tenant_uuid', 'tenant_domain',
        read_only_fields = 'uuid',
        protected_fields = 'tenant',
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'tenant': {'lookup_field': 'uuid', 'view_name': 'exchange-tenants-detail'},
        }
        related_paths = {
            'tenant': ('uuid', 'domain')
        }


class UserPasswordSerializer(serializers.ModelSerializer):

    notify = serializers.BooleanField(write_only=True, required=False)

    class Meta(object):
        model = models.User
        fields = ('password', 'notify')
        read_only_fields = ('password',)


class UserSerializer(BasePropertySerializer):

    notify = serializers.BooleanField(write_only=True, required=False)

    class Meta(BasePropertySerializer.Meta):
        model = models.User
        view_name = 'exchange-users-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'name', 'first_name', 'last_name', 'username', 'password', 'mailbox_size',
            'office', 'phone', 'department', 'company', 'title', 'manager', 'email', 'notify'
        )
        # password update is handled separately in views.py
        read_only_fields = BasePropertySerializer.Meta.read_only_fields + ('password', 'email')
        extra_kwargs = dict(
            manager={'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            **BasePropertySerializer.Meta.extra_kwargs
        )
        protected_fields = BasePropertySerializer.Meta.protected_fields + ('notify',)

    def validate_username(self, value):
        if value:
            if not re.match(r'[a-zA-Z0-9_.-]+$', value) or re.search(r'^\.|\.$', value):
                raise serializers.ValidationError(
                    "The username can contain only letters, numbers, hyphens, underscores and period.")
        return value

    def validate(self, attrs):
        tenant = self.instance.tenant if self.instance else attrs['tenant']

        phone = attrs.get('phone')
        if phone:
            options = tenant.service_project_link.service.settings.options or {}
            phone_regex = options.get('phone_regex')
            if phone_regex and not re.search(phone_regex, phone):
                raise serializers.ValidationError('Invalid phone number.')

        if not self.instance:
            deltas = {
                tenant.Quotas.global_mailbox_size: attrs['mailbox_size'],
                tenant.Quotas.user_count: 1,
            }

            if not tenant.is_username_available(attrs['username']):
                raise serializers.ValidationError(
                    {'username': "This username is already taken."})

        else:
            deltas = {
                tenant.Quotas.global_mailbox_size: attrs['mailbox_size'] - self.instance.mailbox_size,
            }

        try:
            tenant.validate_quota_change(deltas, raise_exception=True)
        except QuotaExceededException as e:
            raise serializers.ValidationError(str(e))

        return attrs

    def create(self, validated_data):
        notify = validated_data.pop('notify')
        user = super(UserSerializer, self).create(validated_data)
        validated_data['notify'] = notify
        return user


class ContactSerializer(BasePropertySerializer):

    class Meta(BasePropertySerializer.Meta):
        model = models.Contact
        view_name = 'exchange-contacts-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'name', 'email', 'first_name', 'last_name',
        )


class GroupSerializer(BasePropertySerializer):

    class Meta(BasePropertySerializer.Meta):
        model = models.Group
        view_name = 'exchange-groups-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'manager', 'manager_uuid', 'manager_name', 'name', 'username', 'email', 'members'
        )
        read_only_fields = BasePropertySerializer.Meta.read_only_fields + ('email',)
        extra_kwargs = dict(
            BasePropertySerializer.Meta.extra_kwargs.items() +
            {
                'manager': {'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
                'members': {'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            }.items()
        )
        related_paths = dict(
            BasePropertySerializer.Meta.related_paths.items() +
            {'manager': ('uuid', 'name')}.items()
        )

    def validate(self, attrs):
        tenant = self.instance.tenant if self.instance else attrs['tenant']

        if not self.instance:
            if not tenant.is_username_available(attrs['username']):
                raise serializers.ValidationError(
                    {'username': "This username is already taken."})

            if attrs['manager'].tenant != tenant:
                raise serializers.ValidationError(
                    {'manager': "Manager user must be form the same tenant as group."})

        for user in attrs['members']:
            if user.tenant != tenant:
                raise serializers.ValidationError(
                    "Users must be from the same tenat as group, can't add %s." % user)

        return attrs
