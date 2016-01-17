def increase_quotas_usage_on_tenant_creation(sender, instance=None, created=False, **kwargs):
    if created:
        spl = instance.service_project_link
        add_quota = spl.add_quota_usage
        add_quota(spl.Quotas.sharepoint_storage, instance.storage_size)


def decrease_quotas_usage_on_tenant_deletion(sender, instance=None, **kwargs):
    spl = instance.service_project_link
    add_quota = spl.add_quota_usage
    add_quota(spl.Quotas.sharepoint_storage, -instance.storage_size)
