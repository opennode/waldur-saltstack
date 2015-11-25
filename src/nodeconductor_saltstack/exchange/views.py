from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from nodeconductor.structure.managers import filter_queryset_for_user
from nodeconductor.structure import views as structure_views
from . import models, serializers


class TenantViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Tenant.objects.all()
    serializer_class = serializers.TenantSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            max_users=serializer.validated_data.get('max_users'),
            mailbox_size=serializer.validated_data.get('mailbox_size'))


class TenantUserViewSet(viewsets.ViewSet):

    def initial(self, request, tenant_uuid, *args, **kwargs):
        super(TenantUserViewSet, self).initial(request, tenant_uuid, *args, **kwargs)
        queryset = filter_queryset_for_user(models.Tenant.objects.all(), request.user)
        self.tenant = get_object_or_404(queryset, uuid=tenant_uuid)
        self.backend = self.tenant.get_backend().exchange

    def get_serializer_context(self):
        return {'tenant': self.tenant, 'request': self.request}

    def list(self, request, tenant_uuid):
        users = self.backend.list_users()
        serializer = serializers.TenantUserSerializer(users, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    def retrieve(self, request, tenant_uuid, pk=None):
        user = self.backend.get_user(pk)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.TenantUserSerializer(user, context=self.get_serializer_context())
        return Response(serializer.data)

    def destroy(self, request, tenant_uuid, pk=None):
        user = self.backend.get_user(pk)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.backend.delete_user(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, tenant_uuid):
        serializer = serializers.TenantUserSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        user = self.backend.create_user(**serializer.validated_data)
        user_data = serializers.TenantUserSerializer(user, context=self.get_serializer_context()).data
        return Response(user_data, status=status.HTTP_201_CREATED)
