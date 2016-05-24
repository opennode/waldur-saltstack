from cStringIO import StringIO
from django.http import HttpResponse

from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from nodeconductor.core.tasks import send_task
from nodeconductor.core.csv import UnicodeDictReader, UnicodeDictWriter
from nodeconductor.structure import views as structure_views

from . import filters, models, serializers
from ..saltstack.utils import sms_user_password
from ..saltstack.views import BasePropertyViewSet, track_exceptions
from log import event_logger


class TenantViewSet(structure_views.BaseOnlineResourceViewSet):
    queryset = models.ExchangeTenant.objects.all()
    serializer_class = serializers.TenantSerializer
    filter_class = filters.TenantFilter

    def perform_provision(self, serializer):
        mailbox_size = serializer.validated_data.pop('mailbox_size')
        resource = serializer.save()
        resource.set_quota_limit(models.ExchangeTenant.Quotas.mailbox_size, mailbox_size)

        backend = resource.get_backend()
        backend.provision(resource, mailbox_size)

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
            old_domain = tenant.domain
            if new_domain != old_domain:
                backend.tenants.change(domain=new_domain)
                tenant.domain = new_domain
                tenant.save()

                event_logger.exchange_tenant.info(
                    'Exchange tenant {tenant_name} domain has been changed from %s to %s.' % (old_domain, new_domain),
                    event_type='exchange_tenant_domain_change',
                    event_context={'tenant': tenant})
            data = serializers.ExchangeDomainSerializer(instance=tenant, context={'request': request}).data
            return Response(data, status=HTTP_200_OK)
        elif request.method == 'GET':
            data = serializers.ExchangeDomainSerializer(instance=tenant, context={'request': request}).data
            return Response(data)

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['get', 'post', 'put'])
    @track_exceptions
    def users(self, request, pk=None, **kwargs):
        tenant = self.get_object()

        if request.method in ('POST', 'PUT'):
            if 'csv' not in request.data:
                return Response({'detail': "Expecting 'csv' parameter as a file or JSON string"},
                                status=HTTP_400_BAD_REQUEST)

            csvfile = request.data['csv']
            if isinstance(csvfile, basestring):
                csvfile = StringIO(csvfile.encode('utf-8'))

            reader = UnicodeDictReader(csvfile)
            tenant_url = self.get_serializer(instance=tenant).data['url']
            try:
                data = [dict(tenant=tenant_url, **row) for row in reader]
            except:
                # A wide exception as CSV is such a great module
                return Response({'detail': "Could not parse CSV payload"},
                                status=HTTP_400_BAD_REQUEST)

            serializer = serializers.UserSerializer(data=data, many=True, context={'request': request})
            serializer.is_valid(raise_exception=True)

            mailbox_size_sum = sum([user['mailbox_size'] for user in serializer.validated_data])
            mailbox_quota = tenant.quotas.get(name='mailbox_size')
            if mailbox_quota.is_exceeded(mailbox_size_sum):
                return Response({'detail': "Size of users' mailboxes exceeds tenant's quota %s" %
                                 mailbox_quota.limit}, status=HTTP_400_BAD_REQUEST)

            # check if global notification has been requested
            notify_user = request.data.get('notify', False)

            for user in serializer.validated_data:
                del user['tenant']
                send_task('exchange', 'create_user')(
                    tenant_uuid=tenant.uuid.hex,
                    notify=notify_user,
                    **user)

            return Response({'status': "%s users scheduled for creation" % len(serializer.validated_data)})

        elif request.method == 'GET':
            users = models.User.objects.filter(tenant=tenant)
            serializer = serializers.UserSerializer(instance=users, many=True, context={'request': request})

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s_users.csv"' % tenant.backend_id

            exclude = ('url', 'tenant', 'tenant_uuid', 'tenant_domain', 'manager',
                       'notify', 'send_on_behalf_members', 'send_as_members', 'quotas')
            headers = [f for f in serializers.UserSerializer.Meta.fields if f not in exclude]
            writer = UnicodeDictWriter(response, fieldnames=headers)
            writer.writeheader()
            writer.writerows(serializer.data)
            return response

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['post', 'put'])
    @track_exceptions
    def change_quotas(self, request, pk=None, **kwargs):
        tenant = self.get_object()
        backend = tenant.get_backend()

        serializer = serializers.TenantQuotaSerializer(data=request.data, context={'tenant': tenant})
        serializer.is_valid(raise_exception=True)

        old_quota = tenant.quotas.get(name=models.ExchangeTenant.Quotas.mailbox_size)
        new_quota_limit = serializer.validated_data['mailbox_size']
        backend.tenants.change_quotas(mailbox_size=new_quota_limit)
        tenant.set_quota_limit(models.ExchangeTenant.Quotas.mailbox_size, new_quota_limit)

        event_logger.exchange_tenant.info(
            'Exchange tenant {tenant_name} quota has been updated from %s to %s.' % (old_quota.limit, new_quota_limit),
            event_type='exchange_tenant_quota_update',
            event_context={
                'tenant': tenant,
            })

        return Response({'status': 'Tenant quotas were successfully changed.'}, status=HTTP_200_OK)


class PropertyWithMembersViewSet(BasePropertyViewSet):

    # TODO: Add events to `members_create` and `members_update` methods,
    #       remove `members_update_with_db` method.

    def members_create(self, obj, field_name='', add_method=None):
        backend = self.get_backend(obj.tenant)
        members_ids = getattr(obj, field_name).values_list('backend_id', flat=True)

        if members_ids:
            getattr(backend, add_method)(id=obj.backend_id, user_id=','.join(members_ids))
        return members_ids

    def members_update(self, obj, field_name='', add_method=None, del_method=None, list_method=None, data=None):
        backend = self.get_backend(obj.tenant)
        if field_name in data:
            cur_members = getattr(self, 'cur_%s' % field_name)
            new_members = set(u.backend_id for u in data.get(field_name))

            new_users = new_members - cur_members
            if new_users:
                getattr(backend, add_method)(id=obj.backend_id, user_id=','.join(new_users))

            # TODO: replace it with single method deletion when implemented on backend
            for old_user in cur_members - new_members:
                getattr(backend, del_method)(id=obj.backend_id, user_id=old_user)
            return new_users, cur_members - new_members
        return [], []

    def members_list(self, field_name='', list_method=None):
        obj = self.get_object()
        request = self.request
        entities = getattr(obj, field_name).all()

        return Response(serializers.UserSerializer(
            entities, many=True, context={'request': request}).data, status=HTTP_200_OK)

    # XXX: temporary method
    def members_update_with_db(self, request, field_name='', add_method=None, del_method=None):
        obj = self.get_object()
        backend = self.get_backend(obj.tenant)
        members_qs = getattr(obj, field_name)

        serializer = serializers.MembersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_members = set(u.backend_id for u in serializer.validated_data['members'])
        cur_members = set(members_qs.values_list('backend_id', flat=True))

        new_users = new_members - cur_members
        if new_users:
            getattr(backend, add_method)(id=obj.backend_id, user_id=','.join(new_users))
            members_qs.add(*models.User.objects.filter(backend_id__in=new_users))

        old_users = cur_members - new_members
        if old_users:
            getattr(backend, del_method)(id=obj.backend_id, user_id=','.join(old_users))
            members_qs.remove(*models.User.objects.filter(backend_id__in=old_users))

        return new_users, old_users


class UserViewSet(PropertyWithMembersViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_class = filters.UserFilter
    backend_name = 'users'

    def post_create(self, user, serializer, backend_user):
        user.password = backend_user.password
        user.save()

        self.members_create(user, 'send_on_behalf_members', 'add_send_on_behalf')
        self.members_create(user, 'send_as_members', 'add_send_as')

        if serializer.validated_data.get('notify'):
            sms_user_password(user)

    def pre_update(self, user, serializer):
        self.cur_send_on_behalf_members = set(user.send_on_behalf_members.values_list('backend_id', flat=True))
        self.cur_send_as_members = set(user.send_as_members.values_list('backend_id', flat=True))

    def post_update(self, user, serializer):
        self.members_update(
            user, 'send_on_behalf_members', data=serializer.validated_data,
            add_method='add_send_on_behalf', del_method='del_send_on_behalf', list_method='list_send_on_behalf')
        self.members_update(
            user, 'send_as_members', data=serializer.validated_data,
            add_method='add_send_as', del_method='del_send_as', list_method='list_send_as')

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['post', 'put'])
    @track_exceptions
    def password(self, request, pk=None, **kwargs):
        user = self.get_object()
        backend = self.get_backend(user.tenant)
        response = backend.reset_password(id=user.backend_id)
        user.password = response.password
        user.save()

        serializer_class = serializers.UserPasswordSerializer
        serializer = serializer_class(instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('notify'):
            sms_user_password(user)

        event_logger.exchange_user.info(
            'Exchange user {affected_user_name} ({affected_user_email}) password has been reset.',
            event_type='exchange_user_password_reset',
            event_context={
                'affected_user': user,
            })

        return Response(serializer.data, status=HTTP_200_OK)

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['get', 'post', 'put'])
    def sendonbehalf(self, request, pk=None, **kwargs):
        affected_user = self.get_object()
        if request.method in ('POST', 'PUT'):
            new_users_ids, old_users_ids = self.members_update_with_db(
                request, 'send_on_behalf_members',
                add_method='add_send_on_behalf', del_method='del_send_on_behalf')

            for user in models.User.objects.filter(backend_id__in=new_users_ids):
                event_logger.exchange_user_member.info(
                    'Send On Behalf member %s was added to user {affected_user_name} ({affected_user_email})' % user.email,
                    event_type='exchange_user_send_on_behalf_member_add',
                    event_context={
                        'affected_user': affected_user,
                    })

            for user in models.User.objects.filter(backend_id__in=old_users_ids):
                event_logger.exchange_user_member.info(
                    'Send On Behalf member %s was removed from user {affected_user_name} ({affected_user_email})' % user.email,
                    event_type='exchange_user_send_on_behalf_member_remove',
                    event_context={
                        'affected_user': affected_user,
                    })

        return self.members_list('send_on_behalf_members')

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['get', 'post', 'put'])
    def sendas(self, request, pk=None, **kwargs):
        affected_user = self.get_object()
        if request.method in ('POST', 'PUT'):
            new_users_ids, old_users_ids = self.members_update_with_db(
                request, 'send_as_members',
                add_method='add_send_as', del_method='del_send_as')

            for user in models.User.objects.filter(backend_id__in=new_users_ids):
                event_logger.exchange_user_member.info(
                    'Send As member %s was added to user {affected_user_name} ({affected_user_email})' % user.email,
                    event_type='exchange_user_send_as_member_add',
                    event_context={
                        'affected_user': affected_user,
                    })

            for user in models.User.objects.filter(backend_id__in=old_users_ids):
                event_logger.exchange_user_member.info(
                    'Send As member %s was removed from user {affected_user_name} ({affected_user_email})' % user.email,
                    event_type='exchange_user_send_as_member_remove',
                    event_context={
                        'affected_user': affected_user,
                    })

        return self.members_list('send_as_members')


class ContactViewSet(BasePropertyViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filter_class = filters.ContactFilter
    backend_name = 'contacts'


class ConferenceRoomViewSet(BasePropertyViewSet):
    queryset = models.ConferenceRoom.objects.all()
    serializer_class = serializers.ConferenceRoomSerializer
    filter_class = filters.ConferenceRoomFilter
    backend_name = 'conference_rooms'


class GroupViewSet(PropertyWithMembersViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filter_class = filters.GroupFilter
    backend_name = 'groups'

    def update_senders_out(self, group, serializer):
        backend = self.get_backend(group.tenant)
        senders_out = serializer.validated_data.get('senders_out', None)
        if senders_out is not None and senders_out != group.senders_out:
            backend.set_delivery_options(id=group.backend_id, senders_out=senders_out)

    def post_create(self, group, serializer, backend_group):
        self.update_senders_out(group, serializer)
        new_users_ids = self.members_create(group, 'members', 'add_member')

        for user in models.User.objects.filter(backend_id__in=new_users_ids):
            event_logger.exchange_group_member.info(
                'Member %s was added to group {group_name} ({group_email})' % user.email,
                event_type='exchange_group_member_add',
                event_context={
                    'group': group,
                })

    def pre_update(self, group, serializer):
        self.cur_members = set(group.members.values_list('backend_id', flat=True))

    def post_update(self, group, serializer):
        self.update_senders_out(group, serializer)
        new_users_ids, old_users_ids = self.members_update(
            group, 'members', data=serializer.validated_data,
            add_method='add_member', del_method='del_member', list_method='list_members')

        for user in models.User.objects.filter(backend_id__in=new_users_ids):
            event_logger.exchange_group_member.info(
                'Member %s was added to group {group_name} ({group_email})' % user.email,
                event_type='exchange_group_member_add',
                event_context={
                    'group': group,
                })

        for user in models.User.objects.filter(backend_id__in=old_users_ids):
            event_logger.exchange_group_member.info(
                'Member %s was removed from group {group_name} ({group_email})' % user.email,
                event_type='exchange_group_member_remove',
                event_context={
                    'group': group,
                })

    @detail_route(methods=['get'])
    def members(self, request, pk=None, **kwargs):
        return self.members_list('members')

    # XXX: put was added as portal has a temporary bug with widget update
    @detail_route(methods=['get', 'post', 'put'])
    def delivery_members(self, request, pk=None, **kwargs):
        group = self.get_object()
        backend = self.get_backend(group.tenant)
        members_qs = group.delivery_members

        if request.method in ('POST', 'PUT'):
            serializer = serializers.DeliveryMembersSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            new_members = set(serializer.validated_data['members'])
            cur_members = set(members_qs.all())

            new_users = new_members - cur_members
            if new_users:
                backend.add_delivery_members(
                    id=group.backend_id, user_id=','.join([u.backend_id for u in new_users]))
                members_qs.add(*new_users)
                for member in new_users:
                    event_logger.exchange_group_delivery_member.info(
                        'Delivery member %s has been added to exchange group {group_name} ({group_email}).' % member.email,
                        event_type='exchange_group_delivery_member_add',
                        event_context={
                            'group': group
                        })

            old_users = cur_members - new_members
            if old_users:
                backend.del_delivery_members(
                    id=group.backend_id, user_id=','.join([u.backend_id for u in old_users]))
                members_qs.remove(*old_users)
                for member in old_users:
                    event_logger.exchange_group_delivery_member.info(
                        'Delivery member %s has been removed from exchange group {group_name} ({group_email}).' % member.email,
                        event_type='exchange_group_delivery_member_remove',
                        event_context={
                            'group': group
                        })

        return Response(serializers.DeliveryMembersSerializer(
            members_qs.all(), many=True, context={'request': request}).data, status=HTTP_200_OK)
