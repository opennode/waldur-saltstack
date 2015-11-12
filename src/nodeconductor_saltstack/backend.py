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


class SaltStackAPI(object):

    COMMAND = 'powershell.exe -f D:\\SaaS\\bin\\{name}.ps1 {args}'
    MAPPING = {}

    def __init__(self, api_url, username, password, target, cmd_mapping=None):
        self.api_url = api_url.rstrip('/')
        self.target = target
        self.auth = {'username': username, 'password': password, 'eauth': 'pam'}

        if cmd_mapping and isinstance(cmd_mapping, dict):
            self.MAPPING = cmd_mapping

    def request(self, url, data=None):
        if not data:
            data = {}

        data.update(self.auth)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'NodeConductor/%s' % __version__,
        }

        response = requests.post(
            self.api_url + url, data=json.dumps(data).encode(), headers=headers, verify=False)

        if response.ok:
            return response.json()
        else:
            raise SaltStackBackendError(
                "Request to salt API %s failed: %s %s" % (url, response.response, response.text))

    def run_cmd(self, cmd, **kwargs):
        command = self.COMMAND.format(
            name=self.MAPPING.get(cmd) or cmd,
            args=' '.join(['-%s "%s"' % (k, v) for k, v in kwargs.items()]))

        response = self.request('/run', {
            'client': 'local',
            'fun': 'cmd.run',
            'tgt': self.target,
            'arg': command,
        })

        result = json.loads(response['return'][0][self.target])
        if result['Status'] == 'OK':
            return result['Output']
        else:
            raise SaltStackBackendError(
                "Cannot run command %s on %s: %s" % (cmd, self.target, result['Output']))

        return json.loads(result)


class SaltStackBaseBackend(ServiceBackend):

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

    class Exchange(SaltStackAPI):

        MAPPING = {
            'AddUser': None,
            'DelUser': None,
        }

        def list_users(self):
            return []

        def get_user(self, user_id):
            return {}

        def delete_user(self, username):
            return self.run_cmd(
                'DelUser',
                UserName=username,
            )

        def create_user(self, tenant=None, domain=None, username=None, first_name=None, last_name=None):
            return self.run_cmd(
                'AddUser',
                TenantName=tenant,
                TenantDomain=domain,
                UserName=username,
                UserFirstName=first_name,
                UserLastName=last_name,
                DisplayName="%s %s" % (first_name, last_name),
                UserInitials="%s %s" % (first_name[0], last_name[0]),
            )

    class Sharepoint(SaltStackAPI):
        pass

    def __init__(self, settings):
        options = settings.options or {}
        self.settings = settings
        self.exchange = self.Exchange(
            settings.backend_url, settings.username, settings.password,
            options.get('exchange_target', ''), options.get('exchange_mapping'))

        self.sharepoint = self.Sharepoint(
            settings.backend_url, settings.username, settings.password,
            options.get('sharepoint_target', ''), options.get('sharepoint_mapping'))


class SaltStackDummyBackend(SaltStackBaseBackend):
    pass
