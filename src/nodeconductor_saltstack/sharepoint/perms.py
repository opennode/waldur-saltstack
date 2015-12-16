from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('sharepoint.SharepointTenant', structure_perms.resource_permission_logic),
    ('sharepoint.Template', structure_perms.resource_permission_logic),
)
