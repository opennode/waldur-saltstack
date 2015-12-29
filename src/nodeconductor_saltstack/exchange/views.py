from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from nodeconductor.structure import views as structure_views

from ..saltstack.views import BasePropertyViewSet, track_exceptions
from . import filters, models, serializers


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
    filter_class = filters.UserFilter
    backend_name = 'users'

    def post_create(self, user, backend_user):
        user.password = backend_user.password
        user.save()

        user.tenant.add_quota_usage('user_count', 1)
        user.tenant.add_quota_usage('global_mailbox_size', user.mailbox_size)

    def post_update(self, user, serializer):
        backend = self.get_backend(user.tenant)
        new_password = serializer.validated_data.pop('password', None)
        if new_password and user.password != new_password:
            backend.change_password(id=user.backend_id, password=new_password)

        user.tenant.add_quota_usage(
            'global_mailbox_size', serializer.validated_data['mailbox_size'] - user.mailbox_size)

    def post_destroy(self, user):
        user.tenant.add_quota_usage('user_count', -1)
        user.tenant.add_quota_usage('global_mailbox_size', -user.mailbox_size)


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

    @detail_route(methods=['get', 'post', 'delete'])
    @track_exceptions
    def members(self, request, pk=None, **kwargs):
        group = self.get_object()
        backend = self.get_backend(group.tenant)

        if request.method == 'POST':
            serializer = serializers.GroupMemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data['user']
            data = serializers.UserSerializer(instance=user, context={'request': request}).data

            backend.add_member(id=group.backend_id, user_id=user.backend_id)
            return Response(data, status=HTTP_201_CREATED)

        elif request.method == 'DELETE':
            serializer = serializers.GroupMemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            backend.del_member(
                id=group.backend_id,
                user_id=serializer.validated_data['user'].backend_id)
            return Response(status=HTTP_204_NO_CONTENT)

        else:
            user_ids = [u.id for u in backend.list_members(id=group.backend_id)]
            users = models.User.objects.filter(backend_id__in=user_ids)
            data = serializers.UserSerializer(instance=users, many=True, context={'request': request}).data
            return Response(data)
