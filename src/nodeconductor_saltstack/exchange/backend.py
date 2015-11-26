import logging

from nodeconductor.core.tasks import send_task

from ..saltstack.backend import SaltStackBaseAPI, SaltStackBaseBackend


logger = logging.getLogger(__name__)


def parse_size(size_str):
    """ Convert string notation of size to integer in MB """
    MAPPING = {
        'KB': lambda s: float(s) / 1024,
        'MB': lambda s: float(s),
        'GB': lambda s: ExchangeBackend.gb2mb(int(s)),
    }

    size, unit = size_str.split()
    return MAPPING[unit](size)


class TenantAPI(SaltStackBaseAPI):
    # powershell -f AddTenant.ps1 -TenantName TEST -TenantDomain example.com -TenantMailboxSize 3 -TenantMaxUsers 500
    # powershell -f DelTenant.ps1 -TenantName TEST -TenantDomain example.com
    # powershell -f EditDomain.ps1 -TenantName TEST -TenantDomain example.com

    class Methods:
        create = dict(
            name='AddTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'mailbox_size': 'TenantMailboxSize',
                'max_users': 'TenantMaxUsers',
            },
            output={
                'UPNSuffix': 'id',
                'Accepted DomainName': 'domain',
                'DistinguishedName': 'dn',
            },
        )

        delete = dict(
            name='DelTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
        )

        change = dict(
            name='EditDomain',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
        )


class UserAPI(SaltStackBaseAPI):
    # powershell -f AddUser.ps1 -TenantName TEST -TenantDomain example.com -DisplayName "John Jonson" -UserName john.jonson -UserFirstName "John" -UserLastName "Jonson"  -UserInitials "JJ" -UserMailboxSize 4
    # powershell -f DelUser.ps1 -Identity john.jonson@example.com
    # powershell -f DelUser.ps1 -Identity  e88471c7-fcf5-4e12-8163-2a8ad9c87f4b
    # powershell -f EditUser.ps1 -Guid  e88471c7-fcf5-4e12-8163-2a8ad9c87f4b -UserLastName Malkovich
    # powershell -f EditUser.ps1 -Guid e88471c7-fcf5-4e12-8163-2a8ad9c87f4b -UserQuota 3

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
            },
            defaults={
                'tenant': lambda backend, **kw: backend.tenant.name,
                'domain': lambda backend, **kw: backend.tenant.domain,
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
                'tenant': lambda backend, **kw: backend.tenant.name,
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelUser',
            input={
                'id': 'Identity',
                'email': 'Identity',
            },
        )

        change = dict(
            name='EditUser',
            input={
                'id': 'Guid',
                'name': 'UserLastName',
                'mailbox_size': 'UserQuota',
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
    # powershell -f AddContact.ps1 -TenantName TEST -ContactName "Joe Doe" -ContactEmail joe@domain.com -ContactFirstName Joe -ContactLastName Doe
    # powershell -f DelContact.ps1 -ContactID d7760e2a-0430-4767-838a-b57a7ab8852e
    # powershell -f EditContact.ps1 -Guid 5b6d80ea-bb3e-4321-8722-fe8ab17ec649 -ContactEmail alice@test.com
    # powershell -f ContactList.ps1 -TenantName TEST

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
                'tenant': lambda backend, **kw: backend.tenant.name,
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
                'tenant': lambda backend, **kw: backend.tenant.name,
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
                'email': 'ContactEmail',
            },
            **_base
        )


class DistributionGroupAPI(SaltStackBaseAPI):
    # powershell -f AddDistGrp.ps1 -TenantName TEST -TenantDomain example.com -DisplayName "TEST Managers" -Alias mngr -ManagedByUser john.jonson@example.com
    # powershell -f DelDistGrp.ps1 -Id 99b7febb-4efb-4a2e-b183-6a0624e2e2b0
    # powershell -f DelDistGrp.ps1 -Id mngr@example.com
    # powershell -f EditDg.ps1 -Guid 99b7febb-4efb-4a2e-b183-6a0624e2e2b0 -DisplayName "TEST MGR" -EmailAddress itamngr -ManagedByUser jane.falconer@example.com
    # powershell -f AddDgMember.ps1 -Id 99b7febb-4efb-4a2e-b183-6a0624e2e2b0 -MemberId e941ccc0-75cd-46ab-9c03-a4cda0b62b99
    # powershell -f DelDgMember.ps1 -Id mngr@example.com -MemberId john.jonson@example.com
    # powershell -f DelDgMember.ps1 -Id 99b7febb-4efb-4a2e-b183-6a0624e2e2b0 -MemberId e941ccc0-75cd-46ab-9c03-a4cda0b62b99
    # powershell -f DgMemberList.ps1 -Id 99b7febb-4efb-4a2e-b183-6a0624e2e2b0
    # powershell -f DgMemberList.ps1 -Id mngr@example.com
    # powershell -f DgList.ps1 -TenantName TEST

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
            name='AddDistGrp',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'name': 'DisplayName',
                'username': 'Alias',
                'manager': 'ManagedByUser',
            },
            defaults={
                'tenant': lambda backend, **kw: backend.tenant.name,
                'domain': lambda backend, **kw: backend.tenant.domain,
            },
            **_base
        )

        list = dict(
            name='DgList',
            input={
                'tenant': 'TenantName',
            },
            defaults={
                'tenant': lambda backend, **kw: backend.tenant.name,
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelDistGrp',
            input={
                'id': 'Id',
            },
        )

        change = dict(
            name='EditDg',
            input={
                'id': 'Guid',
                'name': 'DisplayName',
                'username': 'EmailAddress',
                'manager': 'ManagedByUser',
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
                'manager': 'Id',
                'user_id': 'MemberId',
                'user_email': 'MemberId',
            },
            **_base
        )

        list_members = dict(
            name='DgMemberList',
            input={
                'id': 'Id',
                'manager': 'Id',
            },
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

    def destroy(self, tenant):
        tenant.schedule_deletion()
        tenant.save()
        send_task('exchange', 'destroy')(tenant.uuid.hex)
