import json
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

    def __init__(self, settings):
        self.settings = settings

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

    def request(self, url, data=None):
        if not data:
            data = {}

        data.update({
            'username': self.settings.username,
            'password': self.settings.password,
            'eauth': 'pam'
        })

        headers = {
            'User-Agent': 'NodeConductor/%s' % __version__,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        url = self.settings.backend_url.rstrip('/') + url
        response = requests.post(url, data=json.dumps(data).encode(), headers=headers, verify=False)

        if response.ok:
            return response.json()
        else:
            raise SaltStackBackendError(
                "Request to salt API %s failed: %s %s" % (url, response.response, response.text))

    def _run_cmd(self, tgt, cmd, **kwargs):
        command = 'powershell.exe -f D:\\SaaS\\bin\\%s.ps1 %s' % (
            self._get_cmd(cmd), ' '.join(['-%s "%s"' % (k, v) for k, v in kwargs.items()]))
        response = self.request('/run', {
            'client': 'local',
            'fun': 'cmd.run',
            'tgt': tgt,
            'arg': command,
        })

        result = json.loads(response['return'][0][tgt])
        if result['Status'] == 'OK':
            return result['Output']
        else:
            raise SaltStackBackendError(
                "Cannot run command %s on %s: %s" % (cmd, tgt, result['Output']))

        return json.loads(result)

    def _get_cmd(self, cmd):
        # https://confluence.nortal.com/pages/viewpage.action?title=Provisioning+scripts&spaceKey=ITACLOUD
        # The list of supported commands with ability to overwrite their backend names
        options = self.settings.options or {}
        MAPPING = options.get('commands_mapping') or {
            'AddUser': None,
            'DelUser': None,
            'SomeCommand': 'SomeCommandFixed',
        }
        return MAPPING.get(cmd) or cmd

    def run_exchange(self, cmd, **kwargs):
        options = self.settings.options or {}
        return self._run_cmd(options.get('exchange_target', ''), cmd, **kwargs)

    def run_sharepoint(self, cmd, **kwargs):
        options = self.settings.options or {}
        return self._run_cmd(options.get('sharepoint_target', ''), cmd, **kwargs)

    def list_users(self):
        return []

    def get_user(self, user_id):
        return {}

    def delete_user(self, username):
        return self.run_exchange(
            'DelUser',
            UserName=username,
        )

    def create_user(self, tenant=None, domain=None, username=None, first_name=None, last_name=None):
        return self.run_exchange(
            'AddUser',
            TenantName=tenant,
            TenantDomain=domain,
            UserName=username,
            UserFirstName=first_name,
            UserLastName=last_name,
            DisplayName="%s %s" % (first_name, last_name),
            UserInitials="%s %s" % (first_name[0], last_name[0]),
        )


class SaltStackDummyBackend(SaltStackBaseBackend):
    pass
