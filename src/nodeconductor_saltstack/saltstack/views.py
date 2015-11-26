from rest_framework import status, viewsets, exceptions
from rest_framework.response import Response

from nodeconductor.structure import views as structure_views

from .backend import SaltStackBackendError
from . import models, serializers


class SaltStackServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.SaltStackService.objects.all()
    serializer_class = serializers.ServiceSerializer


class SaltStackServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.SaltStackServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class BasePropertyViewSet(viewsets.ViewSet):
    serializer_class = NotImplemented
    api_name = NotImplemented

    @property
    def api(self):
        backend = self.resource.get_backend()
        return getattr(backend, self.api_name)

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {'resource': self.resource, 'request': self.request}
        return self.serializer_class(*args, **kwargs)

    def list(self, request, **kwargs):
        try:
            serializer = self.get_serializer(self.api.list(), many=True)
            return Response(serializer.data)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e)

    def retrieve(self, request, pk=None, **kwargs):
        user = self.api.get(pk)
        if user is None:
            raise exceptions.NotFound
        return Response(self.get_serializer(user).data)

    def destroy(self, request, pk=None, **kwargs):
        try:
            self.api.delete(id=pk)
        except SaltStackBackendError as e:
            raise exceptions.APIException(e)
        return Response({'status': 'Deleted'}, status=status.HTTP_202_ACCEPTED)

    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.api.create(**serializer.validated_data)
            user_data = self.get_serializer(user).data
        except SaltStackBackendError as e:
            raise exceptions.APIException(e)

        return Response(user_data, status=status.HTTP_201_CREATED)
