import logging

from ..saltstack.backend import SaltStackBaseAPI, SaltStackBaseBackend, SaltStackBackendError


logger = logging.getLogger(__name__)


class TenantAPI(SaltStackBaseAPI):

    class Methods:
        ADD = 'AddTenant'
        LIST = 'UserList'
        DELETE = 'DelUser'
        CHANGE = 'EditUser'
        STATS = 'MailboxStat'

    class Fields:
        name = 'TenantName'
        domain = 'TenantDomain', 'Accepted DomainName'
        mailbox_size = 'TenantMailboxSize'
        max_users = 'TenantMaxUsers'
        dn = 'DistinguishedName'


class UserAPI(SaltStackBaseAPI):

    class Methods:
        ADD = 'AddUser'
        LIST = 'UserList'
        DELETE = 'DelUser'
        CHANGE = 'EditUser'
        STATS = 'MailboxStat'

    class Fields:
        id = 'Guid'
        email = 'Email Address'
        name = 'DisplayName'
        password = 'TempPassword'
        first_name = 'FirstName'
        last_name = 'LastName'
        mailbox_size = 'MailboxQuota'
        abbreviation = 'DisplayName'
        dn = 'DistinguishedName'


class ExchangeBackend(SaltStackBaseBackend):

    TARGET_OPTION_NAME = 'exchange_target'
    MAPPING_OPTION_NAME = 'exchange_mapping'

    def __init__(self, *args, **kwargs):
        super(ExchangeBackend, self).__init__(*args, **kwargs)

        self.tenants = self.get_api(TenantAPI)
        self.users = self.get_api(UserAPI)

    def provision(self, tenant, domain=None, max_users=None, mailbox_size=None):
        try:
            self.tenants.add(
                name=tenant.name,
                domain=tenant.domain,
                mailbox_size=mailbox_size,
                max_users=max_users)
        except SaltStackBackendError as e:
            logger.exception('Failed to provision tenant %s: %s', tenant.name, e)
            tenant.error_message = str(e)
            tenant.set_erred()
            tenant.save()
        else:
            tenant.state = tenant.States.ONLINE
            tenant.save()
