import django_filters

from nodeconductor.core import filters as core_filters

from . import models


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    username = django_filters.CharFilter(lookup_type='icontains')
    email = django_filters.CharFilter(lookup_type='icontains')
    first_name = django_filters.CharFilter(lookup_type='icontains')
    last_name = django_filters.CharFilter(lookup_type='icontains')
    tenant_uuid = django_filters.CharFilter(name='tenant__uuid')
    tenant = core_filters.URLFilter(
        view_name='sharepoint-tenants-detail',
        name='tenant__uuid',
    )

    class Meta(object):
        model = models.User
        fields = [
            'name',
            'username',
            'email',
            'first_name',
            'last_name',
            'tenant_uuid',
            'tenant',
        ]
        order_by = [
            'name',
            'username',
            'email',
            'first_name',
            'last_name',
            # desc
            '-name',
            '-username',
            '-email',
            '-first_name',
            '-last_name',
        ]


class TenantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    domain = django_filters.CharFilter(lookup_type='icontains')

    class Meta(object):
        model = models.SharepointTenant
        fields = [
            'name',
            'domain',
        ]
        order_by = [
            'name',
            'domain',
            # desc
            '-name',
            '-domain',
        ]
