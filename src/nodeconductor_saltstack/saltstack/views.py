from functools import wraps
from rest_framework import exceptions, filters, permissions, viewsets

from nodeconductor.structure.filters import GenericRoleFilter
from nodeconductor.structure import views as structure_views

from .backend import SaltStackBackendError
from . import models, serializers


class SaltStackServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.SaltStackService.objects.all()
    serializer_class = serializers.ServiceSerializer


class SaltStackServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.SaltStackServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class BasePropertyViewSet(viewsets.ModelViewSet):
    queryset = NotImplemented
    serializer_class = NotImplemented
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_backends = (GenericRoleFilter, filters.DjangoFilterBackend,)


def track_exceptions():
    def decorator(view_fn):
        @wraps(view_fn)
        def wrapped(self, *args, **kwargs):
            try:
                view_fn(self, *args, **kwargs)
            except SaltStackBackendError as e:
                raise exceptions.APIException(e.traceback_str)
        return wrapped
    return decorator
