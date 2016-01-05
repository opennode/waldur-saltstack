
def init_exchange_storage_limit(sender, instance, created, **kwargs):
    """ Initialize SaltStack SPL exchange_storage quota on creation """
    if not created:
        return
    spl = instance
    spl.quotas.create(name='exchange_storage', limit=sender.DEFAULT_EXCHANGE_STORAGE_LIMIT, usage=0)


def increase_quotas_usage_on_tenant_creation(sender, instance=None, created=False, **kwargs):
    if created:
        add_quota = instance.service_project_link.add_quota_usage
        add_quota('exchange_storage', instance.mailbox_size * instance.max_users)


def decrease_quotas_usage_on_tenant_deletion(sender, instance=None, **kwargs):
    add_quota = instance.service_project_link.add_quota_usage
    add_quota('exchange_storage', -instance.mailbox_size * instance.max_users)


def init_quotas_on_tenant_creation(sender, instance=None, created=False, **kwargs):
    if created:
        instance.quotas.create(name='user_count', limit=instance.max_users, usage=0)
        instance.quotas.create(name='global_mailbox_size', limit=instance.mailbox_size * instance.max_users, usage=0)


def increase_tenant_quotas_usage_on_user_creation_or_modification(sender, instance=None, created=False, **kwargs):
    if created:
        instance.tenant.add_quota_usage('user_count', 1)
        instance.tenant.add_quota_usage('global_mailbox_size', instance.mailbox_size * instance.max_users)

    ## TODO: handle update separately -- calculate diff for global_mailbox_size


def decrease_tenant_quotas_usage_on_user_deletion(sender, instance=None, **kwargs):
    instance.tenant.add_quota_usage('user_count', -1)
    instance.tenant.add_quota_usage('global_mailbox_size', -instance.mailbox_size)
