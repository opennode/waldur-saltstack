from nodeconductor.core.tasks import send_task

from ..saltstack.backend import SaltStackBaseAPI, SaltStackBaseBackend


def parse_size(size_str):
    """ Convert string notation of size to a number in MB """
    MAPPING = {
        'KB': lambda s: float(s) / 1024,
        'MB': lambda s: float(s),
        'GB': lambda s: ExchangeBackend.gb2mb(int(s)),
    }

    size, unit = size_str.split()
    return MAPPING[unit](size)


class TenantAPI(SaltStackBaseAPI):

    class Methods:
        create = dict(
            name='AddTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'mailbox_size': 'TenantMailboxSize',
                'max_users': 'TenantMaxUsers',
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
                "Office":  "office",
                "Phone":  "phone",
                "Department":  "department",
                "Company":  "company",
                "Manager":  "manager",
                "Title":  "title",
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

        change_password = dict(
            name='ResetUserPassword',
            input={
                'id': 'Id',
                'password': 'Pwd',
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
                'mailbox_size': 'UserQuota',
                'office': 'UserOffice',
                'phone': 'UserPhone',
                'department': 'UserDepartment',
                'company': 'UserCompany',
                'manager': 'UserManager',
                'title': 'UserTitle',
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


class ExchangeBackend(SaltStackBaseBackend):

    TARGET_OPTION_NAME = 'exchange_target'
    MAPPING_OPTION_NAME = 'exchange_mapping'
    API = {
        'contacts': ContactAPI,
        'groups': DistributionGroupAPI,
        'tenants': TenantAPI,
        'users': UserAPI,
    }

    def __init__(self, *args, **kwargs):
        super(ExchangeBackend, self).__init__(*args, **kwargs)
        self.tenant = kwargs.get('tenant')

    def provision(self, tenant):
        send_task('exchange', 'provision')(tenant.uuid.hex)

    def destroy(self, tenant, force=False):
        tenant.schedule_deletion()
        tenant.save()
        send_task('exchange', 'destroy')(tenant.uuid.hex, force=force)
