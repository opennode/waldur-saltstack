from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from nodeconductor.structure import views as structure_views

from . import filters, models, serializers
from ..saltstack.views import BasePropertyViewSet, track_exceptions


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.ExchangeTenant.objects.all()
    serializer_class = serializers.TenantSerializer
    filter_class = filters.TenantFilter

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(resource)

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['get', 'post', 'put'])
    @track_exceptions
    def domain(self, request, pk=None, **kwargs):
        tenant = self.get_object()
        backend = tenant.get_backend()

        if request.method in ('POST', 'PUT'):
            domain_serializer = serializers.ExchangeDomainSerializer(instance=tenant, data=request.data)
            domain_serializer.is_valid(raise_exception=True)
            new_domain = domain_serializer.validated_data['domain']
            if new_domain != tenant.domain:
                backend.tenants.change(domain=new_domain)
                tenant.domain = new_domain
                tenant.save()
            data = serializers.ExchangeDomainSerializer(instance=tenant, context={'request': request}).data
            return Response(data, status=HTTP_200_OK)
        elif request.method == 'GET':
            data = serializers.ExchangeDomainSerializer(instance=tenant, context={'request': request}).data
            return Response(data)


class UserViewSet(BasePropertyViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_class = filters.UserFilter
    backend_name = 'users'

    def post_create(self, user, serializer, backend_user):
        user.password = backend_user.password
        user.save()

        if serializer.validated_data['notify']:
            user.notify()

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['post', 'put'])
    @track_exceptions
    def password(self, request, pk=None, **kwargs):
        user = self.get_object()
        backend = self.get_backend(user.tenant)
        response = backend.reset_password(id=user.backend_id)
        user.password = response.password
        user.save()

        serializer = serializers.UserPasswordSerializer(instance=user, context={'request': request})
        serializer.is_valid()
        if serializer.validated_data['notify']:
            user.notify()

        return Response(serializer.data, status=HTTP_200_OK)


class ContactViewSet(BasePropertyViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filter_class = filters.ContactFilter
    backend_name = 'contacts'


class GroupViewSet(BasePropertyViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filter_class = filters.GroupFilter
    backend_name = 'groups'

    def post_create(self, group, serializer, backend_group):
        backend = self.get_backend(group.tenant)
        members = group.members.values_list('backend_id', flat=True)
        if members:
            backend.add_member(id=group.backend_id, user_id=','.join(members))

    def post_update(self, group, serializer):
        backend = self.get_backend(group.tenant)
        new_members = set(u.backend_id for u in serializer.validated_data['members'])
        cur_members = set(group.members.values_list('backend_id', flat=True))

        new_users = new_members - cur_members
        if new_users:
            backend.add_member(id=group.backend_id, user_id=','.join(new_users))

        for old_user in cur_members - new_members:
            backend.del_member(id=group.backend_id, user_id=old_user)

    @detail_route(methods=['get'])
    def members(self, request, pk=None, **kwargs):
        group = self.get_object()

        return Response(serializers.UserSerializer(
            group.members.all(), many=True, context={'request': request}).data, status=HTTP_200_OK)
