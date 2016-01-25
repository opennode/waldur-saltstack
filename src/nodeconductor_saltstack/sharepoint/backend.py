from nodeconductor.core.tasks import send_task

from ..saltstack.backend import SaltStackBaseAPI, SaltStackBaseBackend
from .models import Template


class TenantAPI(SaltStackBaseAPI):

    class Methods:
        create = dict(
            name='AddTenant',
            input={
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
            },
            output={
                'Tenant Database': 'db',
                'DistinguishedName': 'dn',
                'UPNSuffix': 'upn_suffix',
            },
        )

        delete = dict(
            name='DelTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
            defaults={
                'tenant': "{backend.tenant.name}",
                'domain': "{backend.tenant.domain}",
            },
        )

        change_quota = dict(
            name='EditSiteCollectionQuota',
            input={
                'domain': 'TenantDomain',
                'storage_size': 'MainSiteSizeQuota',
                'user_count': 'NumberOfUsers',
            },
            defaults={
                'domain': "{backend.tenant.domain}",
            },
        )

        check = dict(
            name='CheckTenant',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
        )

        storage_size_usage = dict(
            name='StorageUsage',
            input={
                'domain': 'TenantDomain',
            },
            output='*',
            defaults={
                'domain': '{backend.tenant.domain}'
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
            many=True,
        )


class SiteCollectionAPI(SaltStackBaseAPI):

    class Methods:
        _base = dict(
            output={
                'URL': 'url',
                'StorageMax MB': 'max_quota',
                'StorageWarning MB': 'warn_quota',
                'StorageUsage MB': 'usage',
            },
        )

        create = dict(
            name='AddSiteCollection',
            input={
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
                'site_url': 'RelativeSiteUrl',
                'name': 'SiteName',
                'description': 'SiteDesc',
                'template_code': 'SiteTemplate',
                'admin_id': 'SiteAdmin',
                'max_quota': 'MaxQuota',
            },
            defaults={
                'domain': '{backend.tenant.domain}',
                'backend_id': '{backend.tenant.backend_id}'
            },
            **_base
        )

        create_main = dict(
            name='AddMainSiteCollection',
            input={
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
                'name': 'SiteName',
                'description': 'SiteDesc',
                'template_code': 'SiteTemplate',
                'admin_id': 'SiteAdmin',
                'max_quota': 'MaxQuota',
                'user_count': 'MaxNumberOfUsers',
            },
            defaults={
                'domain': "{backend.tenant.domain}",
                'backend_id': '{backend.tenant.backend_id}'
            },
            **_base
        )

        list = dict(
            name='ListAllTenantSites',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
            defaults={
                'tenant': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelSiteCollectionCollection',
            input={
                'url': 'SiteUrl',
            },
        )


class UserAPI(SaltStackBaseAPI):

    class Methods:
        _base = dict(
            output={
                'ObjectGUID': 'id',
                'EmailAddress': 'email',
                'DisplayName': 'name',
                'FirstName': 'first_name',
                'LastName': 'last_name',
                'userPrincipalName': 'login',
                'DistinguishedName': 'dn',
                'SamAccountName': 'admin_id',
                'UserPassword': 'password',
            },
        )

        list = dict(
            name='ListAllUsers',
            input={
                'tenant': 'TenantName',
                'domain': 'TenantDomain',
            },
            defaults={
                'tenant': "{backend.tenant.name}",
                'domain': "{backend.tenant.domain}",
            },
            many=True,
            **_base
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
                'email': 'UserEmail',
            },
            defaults={
                'tenant': "{backend.tenant.name}",
                'domain': "{backend.tenant.domain}",
                'name': "{username}",
            },
            **_base
        )

        change_password = dict(
            name='ResetUserPassword',
            input={
                'id': 'Id',
                'password': 'Pwd',
            },
        )

        delete = dict(
            name='DelUser',
            input={
                'id': 'Id',
                'dn': 'Id',
            },
        )

        change = dict(
            name='EditUser',
            input={
                'domain': 'TenantDomain',
                'admin_id': 'SamAccName',
                'name': 'DisplayName',
                'username': 'UserName',
                'first_name': 'UserFirstName',
                'last_name': 'UserLastName',
                'email': 'UserEmail',
            },
            defaults={
                'domain': "{backend.tenant.domain}",
            },
            **_base
        )


class SharepointBackend(SaltStackBaseBackend):

    TARGET_OPTION_NAME = 'sharepoint_target'
    MAPPING_OPTION_NAME = 'sharepoint_mapping'
    API = {
        'site_collections': SiteCollectionAPI,
        'tenants': TenantAPI,
        'templates': TemplateAPI,
        'users': UserAPI,
    }

    def __init__(self, *args, **kwargs):
        super(SharepointBackend, self).__init__(*args, **kwargs)
        self.tenant = kwargs.get('tenant')

    def sync_backend(self):
        cur_tmpls = {t.backend_id: t for t in Template.objects.filter(settings=self.settings)}
        for backend_tmpl in self.templates.list():
            cur_tmpls.pop(backend_tmpl.code, None)
            Template.objects.update_or_create(
                backend_id=backend_tmpl.code,
                settings=self.settings,
                defaults={
                    'name': backend_tmpl.name,
                    'code': backend_tmpl.code,
                })

        map(lambda i: i.delete(), cur_tmpls.values())

    def provision(self, tenant, **kwargs):
        send_task('sharepoint', 'provision')(tenant.uuid.hex, **kwargs)

    def destroy(self, tenant, force=False):
        tenant.schedule_deletion()
        tenant.save()
        send_task('sharepoint', 'destroy')(tenant.uuid.hex, force=force)
