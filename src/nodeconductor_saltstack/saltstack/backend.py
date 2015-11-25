import json
import logging
import requests

from django.utils import six

from nodeconductor.structure import ServiceBackend, ServiceBackendError
from .. import __version__


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

    TARGET_OPTION_NAME = NotImplemented
    MAPPING_OPTION_NAME = NotImplemented

    def get_api(self, api_cls):
        return api_cls(
            self.settings.backend_url, self.settings.username, self.settings.password,
            self.options.get(self.TARGET_OPTION_NAME, ''),
            self.options.get(self.MAPPING_OPTION_NAME))

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
            raise SaltStackBackendError("Unknown target, can't move on")

        if cmd_mapping and isinstance(cmd_mapping, dict):
            self.MAPPING = cmd_mapping

    def request(self, url, data=None):
        if not data:
            data = {}

        data.update(self.auth)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'NodeConductorSaltStack/%s' % __version__,
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

        result = response['return'][0][self.target]
        try:
            result = json.loads(result)
        except ValueError:
            raise SaltStackBackendError(
                "Error during execution of %s on %s: %s" % (cmd, self.target, result))

        if result['Status'] == 'OK':
            return result['Output']
        else:
            raise SaltStackBackendError(
                "Cannot run command %s on %s: %s" % (cmd, self.target, result['Output']))

        return json.loads(result)


class BackendAPIMetaclass(type):
    """ Creates API methods according to provided mappings. """

    @staticmethod
    def obj2dict(obj, reverse=False):
        result = {}
        for key, val in obj.__dict__.items():
            if not key.startswith('_'):
                if reverse:
                    if not isinstance(val, tuple):
                        val = (val,)
                    for v in val:
                        result[v] = key
                else:
                    result[key] = val[0] if isinstance(val, tuple) else val
        return result

    def __new__(cls, name, bases, cls_args):
        fields = cls_args.pop('Fields')
        methods = cls.obj2dict(cls_args.pop('Methods'))
        fields_forth = cls.obj2dict(fields)
        fields_back = cls.obj2dict(fields, reverse=True)

        def create_entity(entity):
            opts = {}
            for key, val in entity.items():
                if key in fields_back:
                    opts[fields_back[key]] = val
                else:
                    logger.debug(
                        "Unknown field %s in method %s.%s output" % (key, name, fn_name.lower()))

            return type(name.replace('API', ''), (object,), opts)

        for fn_name, method_name in methods.items():
            def method_fn(self, **kwargs):
                opts = {}
                for opt, val in kwargs.items():
                    if opt in fields_forth:
                        opts[fields_forth[opt]] = val
                    else:
                        raise NotImplementedError(
                            "Unknow argument %s for method %s.%s" % (opt, name, fn_name.lower()))

                results = self.run_cmd(method_name, **opts)

                if isinstance(results, list):
                    return [create_entity(entity) for entity in results]
                elif isinstance(results, dict):
                    return create_entity(results)
                else:
                    raise RuntimeError(
                        "Wrong output for method %s.%s: %s" % (name, fn_name.lower(), results))

            cls_args[fn_name.lower()] = method_fn

        return super(BackendAPIMetaclass, cls).__new__(cls, name, bases, cls_args)


@six.add_metaclass(BackendAPIMetaclass)
class SaltStackBaseAPI(SaltStackAPI):

    class Methods:
        """ Methods mapping.
            Example:

            class Methods:
                ADD = 'AddUser'
                LIST = 'UserList'
        """

    class Fields:
        """ Fields mapping.
            Example:

            class Fields:
                id = 'Guid'
                email = 'Email Address'
                name = 'DisplayName'
        """
