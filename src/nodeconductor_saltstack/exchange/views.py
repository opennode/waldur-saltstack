from rest_framework import exceptions, filters, permissions, viewsets

from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure.filters import GenericRoleFilter
from nodeconductor.structure import views as structure_views

from ..saltstack.backend import SaltStackBackendError
from .filters import UserFilter
from . import models, serializers


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.ExchangeTenant.objects.all()
    serializer_class = serializers.TenantSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(resource)

    def perform_update(self, serializer):
        tenant = self.get_object()
        backend = tenant.get_backend()
        try:
            backend.tenants.change(domain=serializer.validated_data['domain'])
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            serializer.save()


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_backends = (GenericRoleFilter, filters.DjangoFilterBackend,)
    filter_class = UserFilter

    def perform_create(self, serializer):
        tenant = serializer.validated_data['tenant']
        backend = tenant.get_backend()

        if tenant.state != models.ExchangeTenant.States.ONLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform user creation")

        try:
            backend_user = backend.users.create(
                **{k: v for k, v in serializer.validated_data.items() if k not in ('tenant',)})
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)

        user = serializer.save()
        user.email = backend_user.email
        user.password = backend_user.password
        user.backend_id = backend_user.id
        user.save()

        user.tenant.add_quota_usage('user_count', 1)
        user.tenant.add_quota_usage('global_mailbox_size', user.mailbox_size)

    def perform_update(self, serializer):
        user = self.get_object()
        backend = user.tenant.get_backend()
        try:
            changed = {k: v for k, v in serializer.validated_data.items() if v and getattr(user, k) != v}
            backend.users.change(id=user.backend_id, **changed)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)

        serializer.save()

        user.tenant.add_quota_usage(
            'global_mailbox_size', serializer.validated_data['mailbox_size'] - user.mailbox_size)

    def perform_destroy(self, user):
        backend = user.tenant.get_backend()
        try:
            backend.users.delete(id=user.backend_id)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)

        user.delete()
        user.tenant.add_quota_usage('user_count', -1)
        user.tenant.add_quota_usage('global_mailbox_size', -user.mailbox_size)
