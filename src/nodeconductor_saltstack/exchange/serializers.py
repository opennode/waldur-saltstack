import os
import re
import binascii

from rest_framework import serializers
from rest_framework.compat import OrderedDict

from nodeconductor.core.serializers import AugmentedSerializerMixin
from nodeconductor.quotas.exceptions import QuotaExceededException
from nodeconductor.quotas.serializers import BasicQuotaSerializer
from nodeconductor.structure import serializers as structure_serializers

from ..saltstack.backend import SaltStackBackendError
from ..saltstack.models import SaltStackServiceProjectLink
from ..saltstack.serializers import PhoneValidationMixin
from . import models


class ExchangeDomainSerializer(serializers.ModelSerializer):

    class Meta():
        model = models.ExchangeTenant
        fields = ('domain',)


class TenantSerializer(structure_serializers.PublishableResourceSerializer):
    MAX_TENANT_SIZE = 2 * 1024 * 1024  # 2TB

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='saltstack-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='saltstack-spl-detail',
        queryset=SaltStackServiceProjectLink.objects.all())

    mailbox_size = serializers.IntegerField(
        min_value=1, write_only=True, help_text='Maximum storage size of all tenant mailboxes together, MB')

    quotas = BasicQuotaSerializer(many=True, read_only=True)

    # Link to Outlook Web Access
    owa_url = serializers.SerializerMethodField()

    # Link to Exchange Control Panel
    ecp_url = serializers.SerializerMethodField()

    def get_owa_url(self, tenant):
        return tenant.service_project_link.service.settings.options.get('owa_url', 'Unknown')

    def get_ecp_url(self, tenant):
        return tenant.service_project_link.service.settings.options.get('ecp_url', 'Unknown')

    class Meta(structure_serializers.PublishableResourceSerializer.Meta):
        model = models.ExchangeTenant
        view_name = 'exchange-tenants-detail'
        protected_fields = structure_serializers.PublishableResourceSerializer.Meta.protected_fields + (
            'domain', 'mailbox_size',
        )
        fields = structure_serializers.PublishableResourceSerializer.Meta.fields + (
            'domain', 'quotas', 'owa_url', 'ecp_url', 'mailbox_size',
        )

    def validate_mailbox_size(self, value):
        if value * .9 > self.MAX_TENANT_SIZE:
            raise serializers.ValidationError("Total mailbox size should be lower than 2 TB")
        return value

    def validate(self, attrs):
        if not self.instance:
            spl = attrs['service_project_link']

            spl_storage_quota = spl.quotas.get(name=spl.Quotas.exchange_storage)
            if spl_storage_quota.is_exceeded(delta=attrs['mailbox_size']):
                storage_left = spl_storage_quota.limit - spl_storage_quota.usage
                raise serializers.ValidationError({
                    'mailbox_size': ("Service project link quota exceeded: Total mailbox size should be lower than %s MB"
                                     % storage_left)
                })

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
            fields.pop('ecp_url', None)

        return fields


# should be initialized with tenant in context
class TenantQuotaSerializer(serializers.Serializer):
    mailbox_size = serializers.FloatField(min_value=1, write_only=True, help_text='Maximum mailbox storage size, MB.')

    def validate_mailbox_size(self, value):
        tenant = self.context['tenant']

        mailbox_size_quota = tenant.quotas.get(name=models.ExchangeTenant.Quotas.mailbox_size)
        if value < mailbox_size_quota.usage:
            raise serializers.ValidationError('Global mailbox size limit cannot be lower than current usage.')

        diff = value - mailbox_size_quota.limit
        spl = tenant.service_project_link
        spl_storage_quota = spl.quotas.get(name=spl.Quotas.exchange_storage)
        if diff > 0 and spl_storage_quota.is_exceeded(delta=diff):
            storage_left = spl_storage_quota.limit - spl_storage_quota.usage
            raise serializers.ValidationError(
                "Service project link quota exceeded: Total mailbox size should be lower than %s MB" % storage_left)
        return value


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


class MembersSerializer(serializers.Serializer):

    members = serializers.HyperlinkedRelatedField(
        queryset=models.User.objects.all(),
        view_name='exchange-users-detail',
        lookup_field='uuid',
        write_only=True,
        many=True)


class UserPasswordSerializer(serializers.ModelSerializer):

    notify = serializers.BooleanField(write_only=True, required=False)

    class Meta(object):
        model = models.User
        fields = ('password', 'notify')
        read_only_fields = ('password',)


class UsernameValidationMixin(object):

    def validate_username(self, value):
        if value:
            if not re.match(r'[a-zA-Z0-9_.-]+$', value) or re.search(r'^\.|\.$', value):
                raise serializers.ValidationError(
                    "The username can contain only letters, numbers, hyphens, underscores and period.")
        return value

    def validate(self, attrs):
        attrs = super(UsernameValidationMixin, self).validate(attrs)
        tenant = self.instance.tenant if self.instance else attrs['tenant']
        exclude = self.instance.username if self.instance else None

        if 'username' in attrs and not tenant.is_username_available(attrs['username'], exclude=exclude):
            raise serializers.ValidationError(
                {'username': "This username is already taken."})

        return attrs


class MailboxExchangePropertySerializer(BasePropertySerializer):

    mailbox_size = serializers.IntegerField(
        min_value=1, help_text='Maximum storage size of all tenant mailboxes together, MB')

    quotas = BasicQuotaSerializer(many=True, read_only=True)

    class Meta(BasePropertySerializer.Meta):
        fields = BasePropertySerializer.Meta.fields + ('mailbox_size', 'quotas',)

    def validate(self, attrs):
        attrs = super(MailboxExchangePropertySerializer, self).validate(attrs)
        tenant = self.instance.tenant if self.instance else attrs['tenant']

        quota = attrs['mailbox_size']
        if self.instance:
            quota -= self.instance.mailbox_size

        try:
            tenant.validate_quota_change({tenant.Quotas.mailbox_size: quota}, raise_exception=True)
        except QuotaExceededException as e:
            raise serializers.ValidationError(str(e))

        return attrs


class UserSerializer(UsernameValidationMixin, PhoneValidationMixin, MailboxExchangePropertySerializer):

    notify = serializers.BooleanField(write_only=True, required=False)

    class Meta(MailboxExchangePropertySerializer.Meta):
        model = models.User
        view_name = 'exchange-users-detail'
        fields = MailboxExchangePropertySerializer.Meta.fields + (
            'name', 'first_name', 'last_name', 'username', 'password',
            'office', 'phone', 'department', 'company', 'title', 'manager', 'email', 'notify',
            'send_on_behalf_members', 'send_as_members',
        )
        # password update is handled separately in views.py
        read_only_fields = MailboxExchangePropertySerializer.Meta.read_only_fields + ('password', 'email')
        extra_kwargs = dict(
            manager={'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            send_as_members={'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            send_on_behalf_members={'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            **MailboxExchangePropertySerializer.Meta.extra_kwargs
        )
        protected_fields = MailboxExchangePropertySerializer.Meta.protected_fields + ('notify',)

    def get_fields(self):
        fields = super(UserSerializer, self).get_fields()
        fields['send_as_members'].required = False
        fields['send_on_behalf_members'].required = False
        return fields

    def create(self, validated_data):
        notify = validated_data.pop('notify', False)
        user = super(UserSerializer, self).create(validated_data)
        validated_data['notify'] = notify
        return user


class ContactSerializer(BasePropertySerializer):

    email = serializers.EmailField(required=True)

    class Meta(BasePropertySerializer.Meta):
        model = models.Contact
        view_name = 'exchange-contacts-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'name', 'email', 'first_name', 'last_name',
        )


class ConferenceRoomSerializer(UsernameValidationMixin, PhoneValidationMixin, MailboxExchangePropertySerializer):

    class Meta(MailboxExchangePropertySerializer.Meta):
        model = models.ConferenceRoom
        view_name = 'exchange-conference-rooms-detail'
        fields = MailboxExchangePropertySerializer.Meta.fields + (
            'name', 'username', 'email', 'location', 'phone'
        )
        read_only_fields = MailboxExchangePropertySerializer.Meta.read_only_fields + ('email',)


class DeliveryMembersSerializer(serializers.BaseSerializer):

    SERIALIZERS = (UserSerializer, ContactSerializer)

    def to_internal_value(self, data):
        members = data.get('members', [])
        result = []
        for member in members:
            for serializer in self.SERIALIZERS:
                field = serializers.HyperlinkedRelatedField(
                    queryset=serializer.Meta.model.objects.all(),
                    view_name=serializer.Meta.view_name,
                    lookup_field='uuid')

                try:
                    result.append(field.to_internal_value(member))
                except serializers.ValidationError:
                    continue
                else:
                    break
            else:
                raise serializers.ValidationError("Invalid hyperlink - Incorrect URL match.")

        return OrderedDict(members=result)

    def to_representation(self, instance):
        for serializer in self.SERIALIZERS:
            if isinstance(instance, serializer.Meta.model):
                return serializer(instance, context=self.context).data

        raise serializers.ValidationError('Unsupported object: %s' % instance)


class GroupSerializer(UsernameValidationMixin, BasePropertySerializer):

    delivery_members = DeliveryMembersSerializer(many=True, read_only=True)

    class Meta(BasePropertySerializer.Meta):
        model = models.Group
        view_name = 'exchange-groups-detail'
        fields = BasePropertySerializer.Meta.fields + (
            'manager', 'manager_uuid', 'manager_name', 'name', 'username', 'email',
            'senders_out', 'members', 'delivery_members'
        )
        read_only_fields = BasePropertySerializer.Meta.read_only_fields + ('email', 'delivery_members')
        extra_kwargs = dict(
            manager={'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            members={'lookup_field': 'uuid', 'view_name': 'exchange-users-detail'},
            **BasePropertySerializer.Meta.extra_kwargs
        )
        related_paths = dict(
            BasePropertySerializer.Meta.related_paths.items() +
            {'manager': ('uuid', 'name')}.items()
        )

    def get_fields(self):
        fields = super(GroupSerializer, self).get_fields()
        fields['members'].required = False
        return fields

    def validate(self, attrs):
        attrs = super(GroupSerializer, self).validate(attrs)
        tenant = self.instance.tenant if self.instance else attrs['tenant']

        if not self.instance:
            if attrs['manager'].tenant != tenant:
                raise serializers.ValidationError(
                    {'manager': "Manager user must be form the same tenant as group."})

        for user in attrs.get('members', []):
            if user.tenant != tenant:
                raise serializers.ValidationError(
                    "Users must be from the same tenant as group, can't add %s." % user)

        return attrs
