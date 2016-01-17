def increase_quotas_usage_on_tenant_creation(sender, instance=None, created=False, **kwargs):
    if created:
        add_quota = instance.service_project_link.add_quota_usage
        add_quota('sharepoint_storage', instance.storage_size)


def decrease_quotas_usage_on_tenant_deletion(sender, instance=None, **kwargs):
    add_quota = instance.service_project_link.add_quota_usage
    add_quota('sharepoint_storage', -instance.storage_size)
