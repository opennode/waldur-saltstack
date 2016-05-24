from nodeconductor.core.tasks import send_task

from ..saltstack.backend import SaltStackBaseAPI, SaltStackBaseBackend, parse_size

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
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
            },
            defaults={
                'backend_id': "{backend.tenant.backend_id}",
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
                'Quota Usage [MB]': 'storage_usage',
                'Quota Size [MB]': 'storage_limit',
            },
            clean={
                'Quota Usage [MB]': int,
                'Quota Size [MB]': int,
            },
        )

        create = dict(
            name='AddSiteCollection',
            input={
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
                'site_url': 'SiteCollectionName',
                'name': 'SiteName',
                'description': 'SiteDesc',
                'template_code': 'SiteTemplate',
                'admin_id': 'SiteAdmin',
                'storage': 'SiteQuotaSize',
            },
            defaults={
                'domain': '{backend.tenant.domain}',
                'backend_id': '{backend.tenant.backend_id}'
            },
            **_base
        )

        create_main = dict(
            name='AddTenantSiteCollections',
            input={
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
                'admin_id': 'SiteAdmin',
                'name': 'SiteName',
                'description': 'SiteDesc',
                'template_code': 'SiteTemplate',
                'storage': 'StorageQuotaSize',
            },
            defaults={
                'domain': "{backend.tenant.domain}",
                'backend_id': '{backend.tenant.backend_id}'
            },
            output={
                "My Site URL":  "personal_site_collection_url",
                "My Site Quota [MB]":  'personal_site_collection_storage',
                "My Site Template": "personal_site_collection_template_code",
                "Main Site URL":  "main_site_collection_url",
                "Main Site Quota [MB]": "main_site_collection_storage",
                "Admin Site Admin URL": "admin_site_collection_url",
                "Admin Site Quota [MB]": "admin_site_collection_storage",
                "Admin Site Template": "admin_site_collection_template_code",
                "Site Subscription ID":  "subscription_id",
            },
            clean={
                "Admin Site Quota [MB]": int,
                "Main Site Quota [MB]": int,
                "My Site Quota [MB]": int,
            }
        )

        list = dict(
            name='ListAllTenantSites',
            input={
                'domain': 'TenantDomain',
            },
            defaults={
                'domain': "{backend.tenant.domain}",
            },
            many=True,
            **_base
        )

        delete = dict(
            name='DelSiteCollection',
            input={
                'url': 'SiteCollectionUrl',
            },
        )

        set_storage = dict(
            name='EditSiteQuota',
            input={
                'url': 'SiteCollectionUrl',
                'storage': 'SiteQuotaSize',
            },
        )

        check = dict(
            name='CheckPersonalSiteCollection',
            input={
                'url': 'SiteUrl',
            },
            output={
                'QuotaSize': 'quota_limit',
                'SiteTemplate': 'template_code',
                'QuotaUsage': 'quota_usage',
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
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
            },
            defaults={
                'backend_id': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
            },
            many=True,
            **_base
        )

        create = dict(
            name='AddUser',
            input={
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
                'name': 'DisplayName',
                'username': 'UserName',
                'first_name': 'UserFirstName',
                'last_name': 'UserLastName',
                'email': 'UserEmail',
            },
            defaults={
                'backend_id': "{backend.tenant.backend_id}",
                'domain': "{backend.tenant.domain}",
            },
            output=dict(
                PersonalSiteCollection='personal_site_collection_url',
                **_base['output']
            ),
        )

        reset_password = dict(
            name='ResetUserPassword',
            input={
                'id': 'Id',
            },
            output={
                'UserPassword': 'password',
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
                'backend_id': 'TenantName',
                'domain': 'TenantDomain',
                'id': 'Id',
                'name': 'DisplayName',
                'username': 'UserName',
                'first_name': 'UserFirstName',
                'last_name': 'UserLastName',
                'email': 'UserEmail',
            },
            defaults={
                'backend_id': "{backend.tenant.backend_id}",
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

        storage = self.service_settings.get_storage()
        self.settings.set_quota_limit(self.settings.Quotas.sharepoint_storage, storage.used + storage.free)
        self.settings.set_quota_usage(self.settings.Quotas.sharepoint_storage, storage.used)

    def provision(self, tenant, **kwargs):
        send_task('sharepoint', 'provision')(tenant.uuid.hex, **kwargs)

    def destroy(self, tenant, force=False):
        tenant.schedule_deletion()
        tenant.save()
        send_task('sharepoint', 'destroy')(tenant.uuid.hex, force=force)
