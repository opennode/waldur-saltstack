from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure import views as structure_views

from ..saltstack.views import BasePropertyViewSet, track_exceptions
from .filters import UserFilter
from . import models, serializers


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
    filter_class = UserFilter

    @track_exceptions
    def perform_create(self, serializer):
        tenant = serializer.validated_data['tenant']
        backend = tenant.get_backend()

        if tenant.state != models.ExchangeTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform user creation")

        backend_user = backend.users.create(
            **{k: v for k, v in serializer.validated_data.items() if k not in ('tenant',)})

        user = serializer.save()
        user.email = backend_user.email
        user.password = backend_user.password
        user.backend_id = backend_user.id
        user.save()

        user.tenant.add_quota_usage('user_count', 1)
        user.tenant.add_quota_usage('global_mailbox_size', user.mailbox_size)

    @track_exceptions
    def perform_update(self, serializer):
        user = self.get_object()
        backend = user.tenant.get_backend()
        changed = {k: v for k, v in serializer.validated_data.items() if v and getattr(user, k) != v}
        backend.users.change(id=user.backend_id, **changed)
        serializer.save()

        user.tenant.add_quota_usage(
            'global_mailbox_size', serializer.validated_data['mailbox_size'] - user.mailbox_size)

    def perform_destroy(self, user):
        backend = user.tenant.get_backend()
        backend.users.delete(id=user.backend_id)

        user.delete()
        user.tenant.add_quota_usage('user_count', -1)
        user.tenant.add_quota_usage('global_mailbox_size', -user.mailbox_size)
