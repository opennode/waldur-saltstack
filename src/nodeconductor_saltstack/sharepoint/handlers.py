
def init_sharepoint_storage_limit(sender, instance, created, **kwargs):
    """ Initialize SaltStack SPL sharepoint_storage quota on creation """
    if not created:
        return
    spl = instance
    spl.quotas.create(name='sharepoint_storage', limit=sender.DEFAULT_SHAREPOINT_STORAGE_LIMIT, usage=0)
