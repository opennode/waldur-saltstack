
from ..saltstack.backend import SaltStackAPI, SaltStackBaseBackend
from .models import Tenant


class ExchangeAPI(SaltStackAPI):

    MAPPING = {
        'AddTenant': None,
        'DelTenant': None,
        'EditDomain': None,
        'AddUser': None,
        'DelUser': None,
        'EditUser': None,
        'MailboxStat': None,
        'UserList': None,
        'AddContact': None,
        'DelContact': None,
        'EditContact': None,
        'ContactList': None,
        'AddDistGrp': None,
        'DelDistGrp': None,
        'AddDgMember': None,
        'DelDgMember': None,
        'DgMemberList': None,
        'DgList': None,
    }

    def create_tenant(self, name=None, domain=None, mailbox_size=None, max_users=None):
        return self.run_cmd(
            'AddTenant',
            TenantName=name,
            TenantDomain=domain,
            TenantMailboxSize=mailbox_size,
            TenantMaxUsers=max_users)

    def delete_tenant(self, name=None, domain=None):
        return self.run_cmd(
            'DelTenant',
            TenantName=name,
            TenantDomain=domain)

    def change_tenant(self, name=None, new_domain=None):
        return self.run_cmd(
            'EditDomain',
            TenantName=name,
            TenantDomain=new_domain)

    def create_user(self, tenant=None, domain=None, username=None, first_name=None, last_name=None, mailbox_size=None):
        return self.run_cmd(
            'AddUser',
            TenantName=tenant,
            TenantDomain=domain,
            UserName=username,
            UserFirstName=first_name,
            UserLastName=last_name,
            UserMailboxSize=mailbox_size.
            DisplayName="%s %s" % (first_name, last_name),
            UserInitials="%s %s" % (first_name[0], last_name[0]))

    def delete_user(self, guid):
        return self.run_cmd('DelUser', Identity=guid)

    def change_user(self, guid, username=None, first_name=None, last_name=None, mailbox_size=None):
        args = {}
        if username:
            args['UserName'] = username
        if first_name:
            args['UserFirstName'] = first_name
        if last_name:
            args['UserLastName'] = last_name
        if mailbox_size:
            args['UserQuota'] = mailbox_size

        if args:
            return self.run_cmd('EditUser', Guid=guid, **args)

    def get_user_stats(self, guid):
        return self.run_cmd('MailboxStat', Id=guid)

    def list_users(self, tenant):
        return self.run_cmd('UserList', TenantName=tenant)

    def get_user(self, guid):
        raise NotImplementedError

    def create_contact(self, tenant=None, email=None, first_name=None, last_name=None):
        return self.run_cmd(
            'AddContact',
            TenantName=tenant,
            ContactEmail=email.
            ContactFirstName=first_name,
            ContactLastName=last_name,
            ContactName="%s %s" % (first_name, last_name))

    def delete_contact(self, guid):
        return self.run_cmd('DelContact', ContactID=guid)

    def change_contact(self, guid, email=None):
        return self.run_cmd('EditContact', Guid=guid, ContactEmail=email)

    def list_contacts(self, tenant):
        return self.run_cmd('ContactList', TenantName=tenant)

    def create_distgroup(self, tenant=None, domain=None, name=None, alias=None, email=None):
        return self.run_cmd(
            'AddDistGrp',
            TenantName=tenant,
            TenantDomain=domain,
            ManagedByUser=email,
            DisplayName=name.
            Alias=alias)

    def delete_distgroup(self, guid):
        return self.run_cmd('DelDistGrp', Id=guid)

    def change_distgroup(self, guid, name=None, alias=None, email=None):
        args = {}
        if name:
            args['DisplayName'] = name
        if alias:
            args['EmailAddress'] = alias
        if email:
            args['ManagedByUser'] = email

        if args:
            return self.run_cmd('EditDg', Guid=guid, **args)

    def distgroup_add(self, guid, muid):
        return self.run_cmd('AddDgMember', Id=guid, MemberId=muid)

    def distgroup_del(self, guid, muid):
        return self.run_cmd('DelDgMember', Id=guid, MemberId=muid)

    def list_distgroup_members(self, guid):
        return self.run_cmd('DgMemberList', Id=guid)

    def list_distgroups(self, tenant):
        return self.run_cmd('DgList', TenantName=tenant)


class ExchangeBackend(SaltStackBaseBackend):

    @property
    def api(self):
        return self._get_api(ExchangeAPI, 'exchange_target', 'exchange_mapping')

    def provision(self, tenant, domain=None, max_users=None, mailbox_size=None):
        self.api.create_tenant(
            name=tenant.name,
            domain=tenant.domain,
            mailbox_size=mailbox_size,
            max_users=max_users)

        tenant.state = tenant.States.ONLINE
        tenant.save()
