from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('saltstack.SaltStackService', structure_perms.service_permission_logic),
    ('saltstack.SaltStackServiceProjectLink', structure_perms.service_project_link_permission_logic),
)

property_permission_logic = structure_perms.property_permission_logic('tenant')
