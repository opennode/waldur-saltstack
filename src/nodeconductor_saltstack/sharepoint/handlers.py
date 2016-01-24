from .tasks import sync_tenant_storage_size_quota


def increase_quotas_usage_on_tenant_creation(sender, instance=None, created=False, **kwargs):
    if created:
        spl = instance.service_project_link
        add_quota = spl.add_quota_usage
        add_quota(spl.Quotas.sharepoint_storage, instance.storage_size)


def decrease_quotas_usage_on_tenant_deletion(sender, instance=None, **kwargs):
    spl = instance.service_project_link
    add_quota = spl.add_quota_usage
    add_quota(spl.Quotas.sharepoint_storage, -instance.storage_size)


def update_tenant_storage_size_quotas_on_site_update(sender, instance, **kwargs):
    site = instance
    sync_tenant_storage_size_quota(site.user.tenant.uuid.hex)


def update_tenant_storage_size_quotas_on_user_update(sender, instance, **kwargs):
    user = instance
    sync_tenant_storage_size_quota(user.tenant.uuid.hex)
