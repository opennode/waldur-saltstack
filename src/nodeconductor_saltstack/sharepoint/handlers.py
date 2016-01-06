
def init_sharepoint_quotas(sender, instance, created, **kwargs):
    """ Initialize SaltStack SPL Sharepoint quotas on creation """
    if not created:
        return
    spl = instance
    spl.quotas.create(name='sharepoint_storage', limit=sender.DEFAULT_SHAREPOINT_STORAGE_LIMIT, usage=0)
    spl.quotas.create(name='sharepoint_tenant_number', limit=sender.DEFAULT_SHAREPOINT_TENANT_NUMBER, usage=0)


def increase_quotas_usage_on_tenant_creation(sender, instance=None, created=False, **kwargs):
    if created:
        add_quota = instance.service_project_link.add_quota_usage
        add_quota('sharepoint_storage', instance.storage_size)
        add_quota('sharepoint_tenant_number', 1)


def decrease_quotas_usage_on_tenant_deletion(sender, instance=None, **kwargs):
    add_quota = instance.service_project_link.add_quota_usage
    add_quota('sharepoint_storage', -instance.storage_size)
    add_quota('sharepoint_tenant_number', -1)
