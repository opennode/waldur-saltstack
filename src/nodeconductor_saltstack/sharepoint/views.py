from rest_framework import exceptions, mixins, viewsets

from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure import views as structure_views

from ..saltstack.backend import SaltStackBackendError
from . import models, serializers


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.SharepointTenant.objects.all()
    serializer_class = serializers.TenantSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(resource)


class TemplateViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    lookup_field = 'uuid'


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'uuid'

    def perform_create(self, serializer):
        tenant = serializer.validated_data['tenant']
        backend = tenant.get_backend()

        if tenant.state != models.SharepointTenant.States.OFFLINE:
            raise IncorrectStateException("Tenant must be in stable state to perform user creation")

        try:
            backend_user = backend.users.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                username=serializer.validated_data['username'],
            )
        except SaltStackBackendError as e:
            raise exceptions.APIException(e.traceback_str)
        else:
            user = serializer.save()
            user.name = backend_user.name
            user.email = backend_user.email
            user.password = backend_user.password
            user.admin_id = backend_user.admin_id
            user.save()
