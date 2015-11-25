
from ..saltstack.backend import SaltStackAPI, SaltStackBaseBackend
from .models import Site


class SharepointAPI(SaltStackAPI):
    pass


class SharepointBackend(SaltStackBaseBackend):

    @property
    def api(self):
        return self._get_api(SharepointAPI, 'sharepoint_target', 'sharepoint_mapping')
