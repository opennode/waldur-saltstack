from functools import wraps
from django.db import IntegrityError, transaction
from rest_framework import exceptions, filters, permissions, viewsets

from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure.filters import GenericRoleFilter
from nodeconductor.structure.models import Resource
from nodeconductor.structure import views as structure_views

from .backend import SaltStackBackendError
from . import models, serializers


def track_exceptions(view_fn):
    @wraps(view_fn)
    def wrapped(*args, **kwargs):
        try:
            return view_fn(*args, **kwargs)
        except (SaltStackBackendError, IntegrityError) as e:
            raise exceptions.APIException(e.traceback_str)
    return wrapped


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
    backend_name = NotImplemented

    def get_backend(self, tenant):
        backend = tenant.get_backend()
        return getattr(backend, self.backend_name)

    def pre_create(self, serializer):
        pass

    def post_create(self, obj, serializer, backend_obj):
        pass

    def pre_update(self, obj, serializer):
        pass

    def post_update(self, obj, serializer):
        pass

    def post_destroy(self, obj):
        pass

    @track_exceptions
    def perform_create(self, serializer):
        tenant = serializer.validated_data['tenant']
        backend = self.get_backend(tenant)

        if tenant.state != Resource.States.ONLINE:
            raise IncorrectStateException(
                "Tenant must be in stable state to perform this operation")

        valid_args = [arg for arg in backend.Methods.create['input'] if arg != 'tenant']
        backend_obj = backend.create(
            **{k: v for k, v in serializer.validated_data.items() if k in valid_args and v is not None})

        with transaction.atomic():
            self.pre_create(serializer)
            obj = serializer.save(backend_id=backend_obj.id)
            self.post_create(obj, serializer, backend_obj)

    @track_exceptions
    def perform_update(self, serializer):
        obj = self.get_object()
        backend = self.get_backend(obj.tenant)
        changed = {
            k: v for k, v in serializer.validated_data.items()
            if v and k in backend.Methods.change['input'] and getattr(obj, k) != v}
        if changed:
            backend.change(id=obj.backend_id, **changed)

        with transaction.atomic():
            self.pre_update(obj, serializer)
            serializer.save()
            self.post_update(obj, serializer)

    @track_exceptions
    def perform_destroy(self, obj):
        backend = self.get_backend(obj.tenant)
        backend.delete(id=obj.backend_id)
        obj.delete()
        self.post_destroy(obj)
