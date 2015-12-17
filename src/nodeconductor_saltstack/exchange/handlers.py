
def init_exchange_storage_limit(sender, instance, created, **kwargs):
    """ Initialize SaltStack SPL exchange_storage quota on creation """
    if not created:
        return
    spl = instance
    spl.quotas.create(name='exchange_storage', limit=sender.DEFAULT_EXCHANGE_STORAGE_LIMIT, usage=0)
