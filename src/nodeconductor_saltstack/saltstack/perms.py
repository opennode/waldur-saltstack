from nodeconductor.core.permissions import FilteredCollaboratorsPermissionLogic
from nodeconductor.structure.models import CustomerRole, ProjectGroupRole, ProjectRole


PERMISSION_LOGICS = (
    ('saltstack.SaltStackService', FilteredCollaboratorsPermissionLogic(
        collaborators_query='customer__roles__permission_group__user',
        collaborators_filter={
            'customer__roles__role_type': CustomerRole.OWNER,
        },
        any_permission=True,
    )),
    ('saltstack.SaltStackServiceProjectLink', FilteredCollaboratorsPermissionLogic(
        collaborators_query=[
            'service__customer__roles__permission_group__user',
            'project__project_groups__roles__permission_group__user',
        ],
        collaborators_filter=[
            {'service__customer__roles__role_type': CustomerRole.OWNER},
            {'project__project_groups__roles__role_type': ProjectGroupRole.MANAGER},
        ],
        any_permission=True,
    )),
)

property_permission_logic = FilteredCollaboratorsPermissionLogic(
    collaborators_query=[
        'tenant__service_project_link__project__roles__permission_group__user',
        'tenant__service_project_link__project__customer__roles__permission_group__user',
    ],
    collaborators_filter=[
        {'tenant__service_project_link__project__roles__role_type': ProjectRole.ADMINISTRATOR},
        {'tenant__service_project_link__project__customer__roles__role_type': CustomerRole.OWNER},
    ],
    any_permission=True,
)
