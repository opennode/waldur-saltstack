import django_filters

from nodeconductor.core import filters as core_filters
from nodeconductor.structure.filters import BaseResourceFilter

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


class TenantFilter(BaseResourceFilter):
    domain = django_filters.CharFilter(lookup_type='icontains')

    class Meta(BaseResourceFilter.Meta):
        model = models.SharepointTenant
        fields = BaseResourceFilter.Meta.fields + ('domain',)
        order_by = BaseResourceFilter.Meta.order_by + ['domain', '-domain']


class SiteCollectionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    description = django_filters.CharFilter(lookup_type='icontains')
    access_url = django_filters.CharFilter(lookup_type='icontains')
    user_uuid = django_filters.CharFilter(name='user__uuid')
    template_code = django_filters.CharFilter(lookup_type='icontains', name='template__code')
    template_name = django_filters.CharFilter(lookup_type='icontains', name='template__name')
    template_uuid = django_filters.CharFilter(name='template__uuid')
    tenant_uuid = django_filters.CharFilter(name='user__tenant__uuid')
    type = django_filters.MultipleChoiceFilter(
        choices=models.SiteCollection.Types.CHOICES,
    )

    class Meta(object):
        model = models.SiteCollection
        fields = [
            'name',
            'description',
            'access_url',
            'user_uuid',
            'type',
            'template_uuid',
            'template_code',
            'template_name',
            'template_uuid',
            'tenant_uuid',
        ]
        order_by = [
            'name',
            'access_url',
            # desc
            '-name',
            '-access_url',
        ]
