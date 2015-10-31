from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from nodeconductor.structure.managers import filter_queryset_for_user
from nodeconductor.structure import views as structure_views
from . import models, serializers


class SaltStackServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.SaltStackService.objects.all()
    serializer_class = serializers.ServiceSerializer


class SaltStackServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.SaltStackServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class DomainViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Domain.objects.all()
    serializer_class = serializers.DomainSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            domain=serializer.validated_data.get('domain'),
            bucket_size=serializer.validated_data.get('bucket_size'),
            mailbox_size=serializer.validated_data.get('mailbox_size'))


class SiteViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Site.objects.all()
    serializer_class = serializers.SiteSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            domain=serializer.validated_data.get('domain'),
            storage_size=serializer.validated_data.get('storage_size'))


class DomainUserViewSet(viewsets.ViewSet):

    def initial(self, request, domain_uuid, *args, **kwargs):
        super(DomainUserViewSet, self).initial(request, domain_uuid, *args, **kwargs)
        queryset = filter_queryset_for_user(models.Domain.objects.all(), request.user)
        self.domain = get_object_or_404(queryset, uuid=domain_uuid)
        self.backend = self.domain.get_backend()

    def get_serializer_context(self):
        return {'domain': self.domain, 'request': self.request}

    def list(self, request, domain_uuid):
        users = self.backend.list_users()
        serializer = serializers.DomainUserSerializer(users, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    def retrieve(self, request, domain_uuid, pk=None):
        user = self.backend.get_user(pk)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.DomainUserSerializer(user, context=self.get_serializer_context())
        return Response(serializer.data)

    def destroy(self, request, domain_uuid, pk=None):
        user = self.backend.get_user(pk)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.backend.delete_user(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, domain_uuid):
        serializer = serializers.DomainUserSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        user = self.backend.create_user(**serializer.validated_data)
        user_data = serializers.DomainUserSerializer(user, context=self.get_serializer_context()).data
        return Response(user_data, status=status.HTTP_201_CREATED)
