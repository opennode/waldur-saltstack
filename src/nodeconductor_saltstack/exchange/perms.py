from nodeconductor.structure import perms as structure_perms
from ..saltstack.perms import property_permission_logic


PERMISSION_LOGICS = (
    ('exchange.ExchangeTenant', structure_perms.resource_permission_logic),
    ('exchange.Group', property_permission_logic),
    ('exchange.Contact', property_permission_logic),
    ('exchange.User', property_permission_logic),
    ('exchange.ConferenceRoom', property_permission_logic),
)
