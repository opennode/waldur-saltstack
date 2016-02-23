from nodeconductor.core.tasks import send_task

from ..saltstack.backend import SaltStackBaseAPI, SaltStackBaseBackend, parse_size


class TenantAPI(SaltStackBaseAPI):

    class Methods:
        create = dict(
            name='AddTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'mailbox_size': 'TenantStorageSize',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
            },
            output={
                'Mailbox Database': 'id',
                'Accepted DomainName': 'domain',
                'DistinguishedName': 'dn',
            },
            clean={
                'Mailbox Database': lambda db: db.replace('_DB', ''),
            },
        )

        delete = dict(
            name='DelTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
            },
        )

        change = dict(
            name='EditDomain',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
            },
        )

        check = dict(
            name='CheckTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
        )

        change_quotas = dict(
            name='EditQuota',
            input={
                'tenant': 'TenantName',
                'mailbox_size': 'MailboxDatabaseSize',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
            },
            output={
                'Mailbox Database Size': 'mailbox_size',
            },
        )


class UserAPI(SaltStackBaseAPI):

    class Methods:
        _base = dict(
            output={
                'Guid': 'id',
                'Email Address': 'email',
                'DisplayName': 'name',
                'TempPassword': 'password',
                'FirstName': 'first_name',
                'LastName': 'last_name',
                'MailboxQuota': 'mailbox_size',
                'DistinguishedName': 'dn',
                'Office': 'office',
                'Phone': 'phone',
                'Department': 'department',
                'Company': 'company',
                'Manager': 'manager',
                'Title': 'title',
            },
            clean={
                'MailboxQuota': parse_size,
            },
        )

        create = dict(
            name='AddUser',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'name': 'DisplayName',
                'username': 'UserName',
                'first_name': 'UserFirstName',
                'last_name': 'UserLastName',
                'abbreviation': 'UserInitials',
                'mailbox_size': 'UserMailboxSize',
                'office': 'UserOffice',
                'phone': 'UserPhone',
                'department': 'UserDepartment',
                'company': 'UserCompany',
                'manager': 'UserManager',
                'title': 'UserTitle',
            },
            paths={
                'manager': 'backend_id',  # manager --> manager.backend_id --> UserManager
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
                'name': "{first_name} {last_name}",
                'abbreviation': "{first_name[0]}{last_name[0]}",
            },
            **_base
        )

        list = dict(
            name='UserList',
            input={
                'tenant': 'TenantName',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelUser',
            input={
                'id': 'Id',
                'email': 'Id',
            },
        )

        reset_password = dict(
            name='ResetUserPassword',
            input={
                'id': 'Id',
            },
            output={
                'TempPassword': 'password',
            },
        )

        change = dict(
            name='EditUser',
            input={
                'id': 'Guid',
                'name': 'DisplayName',
                'username': 'UserName',
                'first_name': 'UserFirstName',
                'last_name': 'UserLastName',
                'abbreviation': 'UserInitials',
                'mailbox_size': 'UserMailboxSize',
                'office': 'UserOffice',
                'phone': 'UserPhone',
                'department': 'UserDepartment',
                'company': 'UserCompany',
                'manager': 'UserManager',
                'title': 'UserTitle',
            },
            paths={
                'manager': 'backend_id',  # manager --> manager.backend_id --> UserManager
            },
            **_base
        )

        stats = dict(
            name='MailboxStat',
            input={
                'id': 'Id',
            },
            output={
                'Quota Limit': 'mailbox_size',
                'MailboxUsage': 'usage',
            },
            clean={
                'Quota Limit': parse_size,
                'MailboxUsage': parse_size,
            },
        )

        list_send_on_behalf = dict(
            name='UserDelegationList',
            input={
                'id': 'Id',
                'send_on_behalf': 'SendOnBehalf',
            },
            many=True,
            defaults={'send_on_behalf': None}, **_base
        )

        add_send_on_behalf = dict(
            name='UserDelegationSB',
            input={
                'id': 'Id',
                'user_id': 'MemberId',
                'add': 'Add',
            },
            many=True,
            defaults={'add': None}, **_base
        )

        del_send_on_behalf = dict(
            name='UserDelegationSB',
            input={
                'id': 'Id',
                'user_id': 'MemberId',
                'del': 'Remove',
            },
            many=True,
            defaults={'del': None}, **_base
        )

        list_send_as = dict(
            name='UserDelegationList',
            input={
                'id': 'Id',
                'send_as': 'SendAs',
            },
            many=True,
            defaults={'send_as': None}, **_base
        )

        add_send_as = dict(
            name='UserDelegationSA',
            input={
                'id': 'Id',
                'user_id': 'MemberId',
                'add': 'Add',
            },
            many=True,
            defaults={'add': None}, **_base
        )

        del_send_as = dict(
            name='UserDelegationSA',
            input={
                'id': 'Id',
                'user_id': 'MemberId',
                'del': 'Remove',
            },
            many=True,
            defaults={'del': None}, **_base
        )


class ContactAPI(SaltStackBaseAPI):

    class Methods:
        _base = dict(
            output={
                'Guid': 'id',
                'EmailAddress': 'email',
                'DisplayName': 'name',
                'DistinguishedName': 'dn',
            },
        )

        create = dict(
            name='AddContact',
            input={
                'tenant': 'TenantName',
                'name': 'ContactName',
                'email': 'ContactEmail',
                'first_name': 'ContactFirstName',
                'last_name': 'ContactLastName',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
                'name': "{first_name} {last_name}",
            },
            **_base
        )

        list = dict(
            name='ContactList',
            input={
                'tenant': 'TenantName',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelContact',
            input={
                'id': 'Id',
            },
        )

        change = dict(
            name='EditContact',
            input={
                'id': 'Guid',
                'name': 'ContactName',
                'email': 'ContactEmail',
                'first_name': 'ContactFirstName',
                'last_name': 'ContactLastName',
            },
            **_base
        )


class DistributionGroupAPI(SaltStackBaseAPI):

    class Methods:
        _base = dict(
            output={
                'Guid': 'id',
                'EmailAddress': 'email',
                'Email Address': 'email',
                'DisplayName': 'name',
                'DistinguishedName': 'dn',
            },
        )

        create = dict(
            name='AddDistGrp',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'name': 'DisplayName',
                'username': 'Alias',
                'manager': 'ManagedByUser',
            },
            paths={
                'manager': 'email',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
            },
            **_base
        )

        list = dict(
            name='DgList',
            input={
                'tenant': 'TenantName',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelDistGrp',
            input={
                'id': 'Id',
                'email': 'Id',
            },
        )

        change = dict(
            name='EditDg',
            input={
                'id': 'Guid',
                'domain': 'TenantDomain',
                'name': 'DisplayName',
                'username': 'Alias',
                'manager': 'ManagedByUser',
            },
            paths={
                'manager': 'email',
            },
            defaults={
                'domain': "{backend.tenant.domain}",
            },
            **_base
        )

        add_member = dict(
            name='AddDgMember',
            input={
                'id': 'Id',
                'user_id': 'MemberId',
            },
            **_base
        )

        del_member = dict(
            name='DelDgMember',
            input={
                'id': 'Id',
                'manager_email': 'Id',
                'user_id': 'MemberId',
                'user_email': 'MemberId',
            },
            **_base
        )

        list_members = dict(
            name='DgMemberList',
            input={
                'id': 'Id',
                'manager_email': 'Id',
            },
            many=True,
            **_base
        )

        list_delivery_members = dict(
            name='DgDeliveryList',
            input={
                'id': 'Id',
            },
            many=True,
            **_base
        )

        add_delivery_members = dict(
            name='DgDeliveryMgmt',
            input={
                'id': 'Id',
                'user_id': 'MemberId',
                'add': 'Add',
            },
            many=True,
            defaults={'add': None}, **_base
        )

        del_delivery_members = dict(
            name='DgDeliveryMgmt',
            input={
                'id': 'Id',
                'user_id': 'MemberId',
                'del': 'Remove',
            },
            many=True,
            defaults={'del': None}, **_base
        )

        set_delivery_options = dict(
            name='DgDeliveryIO',
            input={
                'id': 'Id',
                'senders_out': 'SendersOut',
            },
            **_base
        )


class ConferenceRoomAPI(SaltStackBaseAPI):

    class Methods:
        _base = dict(
            output={
                'Guid': 'id',
                'Email Address': 'email',
                'DisplayName': 'name',
                'DistinguishedName': 'dn',
                'RoomAlias': 'username',
                'Location': 'location',
                'Phone': 'phone',
                'MailboxQuota': 'mailbox_size',

            },
            clean={
                'MailboxQuota': parse_size,
            },
        )

        create = dict(
            name='AddConfRoom',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'name': 'DisplayName',
                'username': 'Alias',
                'location': 'Location',
                'phone': 'Phone',
                'mailbox_size': 'MailboxSize',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
            },
            **_base
        )

        list = dict(
            name='ConfRoomList',
            input={
                'tenant': 'TenantName',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelConfRoom',
            input={
                'id': 'Id',
            },
        )

        change = dict(
            name='EditConfRoom',
            input={
                'id': 'Id',
                'name': 'DisplayName',
                'username': 'Alias',
                'location': 'Location',
                'phone': 'Phone',
                'mailbox_size': 'MailboxSize'
            },
            **_base
        )


class StatsAPI(SaltStackBaseAPI):

    class Methods:

        mailbox = dict(
            name='MailboxStatList',
            input={
                'tenant': 'TenantName',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
            },
            output={
                'Guid': 'user_id',
                'Quota Limit': 'limit',
                'MailboxUsage': 'usage',
                'EmailAddress': 'user_email',
                'Type': 'type',
            },
            clean={
                'Quota Limit': parse_size,
                'MailboxUsage': parse_size,
            },
            many=True,
        )


class ExchangeBackend(SaltStackBaseBackend):

    TARGET_OPTION_NAME = 'exchange_target'
    MAPPING_OPTION_NAME = 'exchange_mapping'
    API = {
        'contacts': ContactAPI,
        'groups': DistributionGroupAPI,
        'tenants': TenantAPI,
        'users': UserAPI,
        'stats': StatsAPI,
        'conference_rooms': ConferenceRoomAPI,
    }

    def __init__(self, *args, **kwargs):
        super(ExchangeBackend, self).__init__(*args, **kwargs)
        self.tenant = kwargs.get('tenant')

    def sync_backend(self):
        storage = self.service_settings.get_storage()
        self.settings.set_quota_limit(self.settings.Quotas.exchange_storage, storage.used + storage.free)
        self.settings.set_quota_usage(self.settings.Quotas.exchange_storage, storage.used)

    def provision(self, tenant, mailbox_size):
        send_task('exchange', 'provision')(tenant.uuid.hex, mailbox_size=mailbox_size)

    def destroy(self, tenant, force=False):
        send_task('exchange', 'destroy')(tenant.uuid.hex, force=force)
