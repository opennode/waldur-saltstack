
from ..saltstack.backend import SaltStackAPI, SaltStackBaseBackend
from .models import Site


class SharepointAPI(SaltStackAPI):
    pass


class SharepointBackend(SaltStackBaseBackend):

    TARGET_OPTION_NAME = 'sharepoint_target'
    MAPPING_OPTION_NAME = 'sharepoint_mapping'
    API = {
        'api': SharepointAPI,
    }
