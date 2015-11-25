import json
import logging
import requests

from nodeconductor.structure import ServiceBackend, ServiceBackendError
from nodeconductor import __version__


logger = logging.getLogger(__name__)


class SaltStackBackendError(ServiceBackendError):
    pass


class SaltStackBackend(object):

    def __init__(self, settings, backend_class=None):
        if not backend_class:
            backend_class = SaltStackBaseBackend
        self.backend = backend_class(settings)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class SaltStackBaseBackend(ServiceBackend):

    @property
    def api(self):
        return self._get_api(SaltStackAPI, '')

    def _get_api(self, api_cls, tgt_name, cmd_mapping=''):
        return api_cls(
            self.settings.backend_url, self.settings.username, self.settings.password,
            self.options.get(tgt_name, ''), self.options.get(cmd_mapping))

    def __init__(self, settings):
        self.options = settings.options or {}
        self.settings = settings


class SaltStackAPI(object):

    COMMAND = 'powershell.exe -f D:\\SaaS\\bin\\{name}.ps1 {args}'
    MAPPING = {}

    def __init__(self, api_url, username, password, target, cmd_mapping=None):
        self.api_url = api_url.rstrip('/')
        self.target = target
        self.auth = {'username': username, 'password': password, 'eauth': 'pam'}

        if not target:
            raise SaltStackBackendError("Unknownt target, can't move on")

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
