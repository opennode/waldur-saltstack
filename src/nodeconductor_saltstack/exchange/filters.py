import django_filters

from .models import User


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    email = django_filters.CharFilter(lookup_type='icontains')
    first_name = django_filters.CharFilter(lookup_type='icontains')
    last_name = django_filters.CharFilter(lookup_type='icontains')
    username = django_filters.CharFilter(lookup_type='icontains')

    class Meta(object):
        model = User
        fields = [
            'name',
            'email',
            'username',
            'first_name',
            'last_name',
            'mailbox_size',
        ]
        order_by = [
            'name',
            'email',
            'username',
            'first_name',
            'last_name',
            'mailbox_size',
            # desc
            '-name',
            '-email',
            '-username',
            '-first_name',
            '-last_name',
            '-mailbox_size',
        ]
