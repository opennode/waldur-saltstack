def increase_exchange_storage_usage_on_tenant_creation(sender, instance=None, created=False, **kwargs):
    if created:
        add_quota = instance.service_project_link.add_quota_usage
        add_quota(instance.service_project_link.Quotas.exchange_storage, instance.mailbox_size * instance.max_users)


def decrease_exchange_storage_usage_on_tenant_deletion(sender, instance=None, **kwargs):
    add_quota = instance.service_project_link.add_quota_usage
    add_quota(instance.service_project_link.Quotas.exchange_storage, -instance.mailbox_size * instance.max_users)


def increase_global_mailbox_size_usage_on_user_creation_or_modification(sender, instance=None, created=False, **kwargs):
    if created:
        instance.tenant.add_quota_usage(instance.tenant.Quotas.global_mailbox_size, instance.mailbox_size)
    else:
        instance.tenant.add_quota_usage(instance.tenant.Quotas.global_mailbox_size,
                                        instance.mailbox_size - instance.tracker.previous('mailbox_size'))


def decrease_global_mailbox_size_usage_on_user_deletion(sender, instance=None, **kwargs):
    instance.tenant.add_quota_usage(instance.tenant.Quotas.global_mailbox_size, -instance.mailbox_size)


def increase_global_mailbox_size_usage_on_conference_room_creation_or_modification(sender, instance=None, created=False,
                                                                                   **kwargs):
    if created:
        instance.tenant.add_quota_usage(instance.tenant.Quotas.global_mailbox_size, instance.mailbox_size)
    else:
        instance.tenant.add_quota_usage(instance.tenant.Quotas.global_mailbox_size,
                                        instance.mailbox_size - instance.tracker.previous('mailbox_size'))


def decrease_global_mailbox_size_usage_on_conference_room_deletion(sender, instance=None, **kwargs):
    instance.tenant.add_quota_usage(instance.tenant.Quotas.global_mailbox_size, -instance.mailbox_size)
