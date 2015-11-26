from django.shortcuts import get_object_or_404

from nodeconductor.structure.managers import filter_queryset_for_user
from nodeconductor.structure import views as structure_views

from ..saltstack.views import BasePropertyViewSet
from . import models, serializers


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.Tenant.objects.all()
    serializer_class = serializers.TenantSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(resource)


class TenantPropertyViewSet(BasePropertyViewSet):

    def initial(self, request, tenant_uuid, *args, **kwargs):
        super(TenantPropertyViewSet, self).initial(request, tenant_uuid, *args, **kwargs)
        queryset = filter_queryset_for_user(models.Tenant.objects.all(), request.user)
        self.resource = get_object_or_404(queryset, uuid=tenant_uuid)


class UserViewSet(TenantPropertyViewSet):
    serializer_class = serializers.UserSerializer
    api_name = 'users'


class ContactViewSet(TenantPropertyViewSet):
    serializer_class = serializers.ContactSerializer
    api_name = 'contacts'


class GroupViewSet(TenantPropertyViewSet):
    serializer_class = serializers.GroupSerializer
    api_name = 'groups'
