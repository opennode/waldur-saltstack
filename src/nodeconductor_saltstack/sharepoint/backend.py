from nodeconductor.core.tasks import send_task

from ..saltstack.backend import SaltStackBaseAPI, SaltStackBaseBackend


class TenantAPI(SaltStackBaseAPI):

    class Methods:
        create = dict(
            name='AddTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
            output={
                'UPNSuffix': 'id',
                'Tenant Database': 'db',
                'WebAppUrl': 'url',
            },
        )

        delete = dict(
            name='DelTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
        )


class TemplateAPI(SaltStackBaseAPI):

    class Methods:
        list = dict(
            name='ListAllTemplates',
            output={
                'Template Name': 'name',
                'Template Code': 'code',
            },
        )


class SiteAPI(SaltStackBaseAPI):

    class Methods:
        create = dict(
            name='InitializeTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
                'name': 'TenantSiteName',
                'description': 'TenantSiteDesc',
                'template_code': 'TenantSiteTemplate',
                'admin_id': 'TenantSiteAdmin',
                'main_quota': 'MainSiteQuota',
                'my_quota': 'MySiteQuota',
            },
            output={
                'Subscription ID': 'id',
                'Admin Site Admin URL': 'admin_url',
                'Main Site URL': 'base_url',
                'My Site URL': 'url',
            },
        )

        list = dict(
            name='ListAllTenantSItes',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
            output={
                'URL': 'url',
                'StorageMax MB': 'storage_limit',
                'StorageWarning MB': 'storage_warn',
            },
        )

        change = dict(
            name='EditSiteQuota',
            input={
                'url': 'SiteUrl',
                'storage_limit': 'MaxQuota',
                'storage_warn': 'WarningQuota',
            },
        )


class UserAPI(SaltStackBaseAPI):

    class Methods:
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
                'email': 'UserEmail',
            },
            defaults={
                'name': "{first_name} {last_name}",
                'abbreviation': "{first_name[0]}{last_name[0]}",
            },
            output={
                'ObjectGUID': 'id',
                'Email Address': 'email',
                'DisplayName': 'name',
                'TempPassword': 'password',
                'FirstName': 'first_name',
                'LastName': 'last_name',
                'Initials': 'abbreviation',
                'DistinguishedName': 'dn',
                'SamAccountName': 'admin_id',
                'TempPassword': 'password',
            },
        )

        delete = dict(
            name='DelUser',
            input={
                'id': 'Id',
                'dn': 'Id',
            },
        )


class SharepointBackend(SaltStackBaseBackend):

    TARGET_OPTION_NAME = 'sharepoint_target'
    MAPPING_OPTION_NAME = 'sharepoint_mapping'
    API = {
        'sites': SiteAPI,
        'tenants': TenantAPI,
        'templates': TemplateAPI,
        'users': UserAPI,
    }

    def __init__(self, *args, **kwargs):
        super(SharepointBackend, self).__init__(*args, **kwargs)
        self.tenant = kwargs.get('tenant')
