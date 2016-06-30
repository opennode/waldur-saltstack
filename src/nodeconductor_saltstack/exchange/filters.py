import django_filters

from nodeconductor.structure.filters import BaseResourceFilter

from . import models


class TenantFilter(BaseResourceFilter):
    domain = django_filters.CharFilter(lookup_type='icontains')

    class Meta(BaseResourceFilter.Meta):
        model = models.ExchangeTenant
        fields = BaseResourceFilter.Meta.fields + ('domain',)
        order_by = BaseResourceFilter.Meta.order_by + ['domain', '-domain']


class ContactFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    email = django_filters.CharFilter(lookup_type='icontains')
    first_name = django_filters.CharFilter(lookup_type='icontains')
    last_name = django_filters.CharFilter(lookup_type='icontains')
    tenant_uuid = django_filters.CharFilter(name='tenant__uuid')

    class Meta(object):
        model = models.Contact
        fields = [
            'name',
            'email',
            'first_name',
            'last_name',
            'tenant_uuid',
        ]


class ConferenceRoomFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    username = django_filters.CharFilter(lookup_type='icontains')
    phone = django_filters.CharFilter(lookup_type='icontains')
    location = django_filters.CharFilter(lookup_type='icontains')
    tenant_domain = django_filters.CharFilter(name='tenant__domain', lookup_type='icontains')
    tenant_uuid = django_filters.CharFilter(name='tenant__uuid')

    class Meta(object):
        model = models.ConferenceRoom
        fields = [
            'name',
            'username',
            'phone',
            'location',
            'tenant_domain',
            'tenant_uuid',
        ]


class GroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    username = django_filters.CharFilter(lookup_type='icontains')
    tenant_domain = django_filters.CharFilter(name='tenant__domain', lookup_type='icontains')
    tenant_uuid = django_filters.CharFilter(name='tenant__uuid')

    class Meta(object):
        model = models.Group
        fields = [
            'name',
            'username',
            'tenant_domain',
            'tenant_uuid',
        ]


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    email = django_filters.CharFilter(lookup_type='icontains')
    first_name = django_filters.CharFilter(lookup_type='icontains')
    last_name = django_filters.CharFilter(lookup_type='icontains')
    username = django_filters.CharFilter(lookup_type='icontains')
    tenant_uuid = django_filters.CharFilter(name='tenant__uuid')

    class Meta(object):
        model = models.User
        fields = [
            'name',
            'email',
            'username',
            'first_name',
            'last_name',
            'tenant_uuid',
        ]
        order_by = [
            'name',
            'email',
            'username',
            'first_name',
            'last_name',
            # desc
            '-name',
            '-email',
            '-username',
            '-first_name',
            '-last_name',
        ]
