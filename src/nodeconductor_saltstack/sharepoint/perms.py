from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import perms as structure_perms
from ..saltstack.perms import property_permission_logic


PERMISSION_LOGICS = (
    ('sharepoint.SharepointTenant', structure_perms.resource_permission_logic),
    ('sharepoint.Template', StaffPermissionLogic(any_permission=True)),
    ('sharepoint.User', property_permission_logic),
    ('sharepoint.SiteCollection', property_permission_logic),
)
