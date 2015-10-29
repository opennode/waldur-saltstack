import logging
import requests

from nodeconductor.structure import ServiceBackend, ServiceBackendError
from nodeconductor import __version__

from .models import Domain, Site


logger = logging.getLogger(__name__)


class SaltStackBackendError(ServiceBackendError):
    pass


class SaltStackBackend(object):

    def __init__(self, settings, *args, **kwargs):
        backend_class = SaltStackDummyBackend if settings.dummy else SaltStackRealBackend
        self.backend = backend_class(settings, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class SaltStackBaseBackend(ServiceBackend):

    def __init__(self, settings, target=None):
        self.settings = settings
        self.target = target

    def provision(self, resource, **kwargs):
        # XXX: to be implemented
        resource.state = resource.States.ONLINE
        resource.save()

        if isinstance(resource, Domain):
            kwargs.update({'bucket_name': resource.name})
        elif isinstance(resource, Site):
            kwargs.update({'site_name': resource.name})
        else:
            raise NotImplementedError


class SaltStackRealBackend(SaltStackBaseBackend):

    def request(self, url, data=None, verify=False, **kwargs):
        headers = {'User-Agent': 'NodeConductor/%s' % __version__,
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'application/json'}

        if not data:
            data = {}

        data['tgt'] = self.target
        data['secretkey'] = self.settings.password

        url = self.settings.backend_url.rstrip('/') + url
        response = requests.post(url, data=data, headers=headers, verify=verify)

        if response.ok:
            result = response.json()
            if not result['success']:
                raise SaltStackBackendError('Wrong response from salt API %s: %s' % (url, response.text))
            else:
                return result
        else:
            raise SaltStackBackendError('Request to salt API %s failed: %s' % (url, response.text))

    def hook(self, name):
        return self.request('/hook/%s' % name)

    def list_users(self):
        return []

    def get_user(self, user_id):
        return {}

    def delete_user(self, user_id):
        pass

    def create_user(self, **kwargs):
        return {}


class SaltStackDummyBackend(SaltStackBaseBackend):
    pass
