from nodeconductor.structure import views as structure_views

from ..saltstack.views import BasePropertyViewSet, track_exceptions
from . import filters, models, serializers


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.ExchangeTenant.objects.all()
    serializer_class = serializers.TenantSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(resource)

    @track_exceptions
    def perform_update(self, serializer):
        tenant = self.get_object()
        backend = tenant.get_backend()
        backend.tenants.change(domain=serializer.validated_data['domain'])
        serializer.save()


class UserViewSet(BasePropertyViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_class = filters.UserFilter
    backend_name = 'users'

    def post_create(self, user, backend_user):
        user.email = backend_user.email
        user.password = backend_user.password
        user.save()

        user.tenant.add_quota_usage('user_count', 1)
        user.tenant.add_quota_usage('global_mailbox_size', user.mailbox_size)

    def post_update(self, user, serializer):
        user.tenant.add_quota_usage(
            'global_mailbox_size', serializer.validated_data['mailbox_size'] - user.mailbox_size)

    def post_destroy(self, user):
        user.tenant.add_quota_usage('user_count', -1)
        user.tenant.add_quota_usage('global_mailbox_size', -user.mailbox_size)


class ContactViewSet(BasePropertyViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filter_class = filters.ContactFilter
    backend_name = 'contacts'
