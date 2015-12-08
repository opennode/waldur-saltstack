import json
import types
import logging
import requests
import functools

from nodeconductor.structure import ServiceBackend, ServiceBackendError
from .. import __version__


logger = logging.getLogger(__name__)


class SaltStackBackendError(ServiceBackendError):

    def __init__(self, message, traceback=None):
        super(SaltStackBackendError, self).__init__(message)
        self.traceback_str = '; '.join(["%s: %s" % (k, v) for k, v in traceback.items()]) if traceback else ''
        self.traceback = traceback


class SaltStackBackend(object):

    def __init__(self, settings, backend_class=None, **kwargs):
        if not backend_class:
            backend_class = SaltStackBaseBackend
        self.backend = backend_class(settings, **kwargs)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class SaltStackBaseBackend(ServiceBackend):

    TARGET_OPTION_NAME = NotImplemented
    MAPPING_OPTION_NAME = NotImplemented
    API = {}

    def __init__(self, settings, **kwargs):
        self.settings = settings

        options = settings.options or {}
        for name, api_cls in self.API.items():
            api = api_cls(
                settings.backend_url, settings.username, settings.password,
                options.get(self.TARGET_OPTION_NAME, ''),
                options.get(self.MAPPING_OPTION_NAME))

            setattr(api, 'backend', self)
            setattr(self, name, api)


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
                "Cannot run command %s on %s: %s" % (cmd, self.target, result['Output']),
                result['Output'])

        return json.loads(result)


class SaltStackBaseAPI(SaltStackAPI):

    class Methods:
        """ Methods mapping.
            Example:

            class Methods:
                # method name as to be used within API
                add = dict(
                    name='AddTenant',  # command name to be called on backend
                    input={  # input arguments mapping
                        'tenant': 'TenantName',
                        'domain': 'TenantDomain',
                        'mailbox_size': 'TenantMailboxSize',
                        'max_users': 'TenantMaxUsers',
                    },
                    output={   # input fields mapping
                        'Accepted DomainName': 'domain',
                        'DistinguishedName': 'dn',
                    },
                )
        """

    def __init__(self, *args, **kwargs):
        super(SaltStackBaseAPI, self).__init__(*args, **kwargs)

        name = self.__class__.__name__
        methods = {k: v for k, v in self.Methods.__dict__.items() if not k.startswith('_')}

        def create_entity(entity, fn_opts):
            out = fn_opts.get('output')
            clean = fn_opts.get('clean')

            if not entity or not out:
                return None

            opts = {}
            for key, val in entity.items():
                if key in out:
                    if clean and key in clean:
                        val = clean[key](val)
                    opts[out[key]] = val
                else:
                    logger.debug(
                        "Unknown field '%s' in method %s.%s output" % (key, name, fn_name.lower()))

            class Entity(object):
                def __init__(self, opts):
                    self.__dict__ = opts

                def __repr__(self):
                    reprkeys = sorted(k for k in self.__dict__.keys())
                    info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
                    return "<%s %s>" % (self.__class__.__name__, info)

            return type(name.replace('API', ''), (Entity,), {})(opts)

        def method_fn(self, fn_opts=(), **kwargs):
            inp = fn_opts.get('input') or {}
            func = fn_opts['name']
            opts = {}

            if 'defaults' in fn_opts:
                for opt in fn_opts['defaults']:
                    if opt not in kwargs:
                        fn = fn_opts['defaults'][opt]
                        if isinstance(fn, basestring):
                            kwargs[opt] = fn.format(**kwargs)
                        elif isinstance(fn, types.FunctionType):
                            kwargs[opt] = fn(self.backend, **kwargs)
                        else:
                            raise NotImplementedError(
                                "Unknown default argument '%s' for method %s.%s" % (opt, name, func))

            for opt, val in kwargs.items():
                if opt in inp:
                    opts[inp[opt]] = val
                else:
                    raise NotImplementedError(
                        "Unknown argument '%s' for method %s.%s" % (opt, name, func))

            results = self.run_cmd(func, **opts)

            if isinstance(results, list):
                entities = [create_entity(entity, fn_opts) for entity in results]
                return entities if fn_opts.get('many') else entities[0]
            elif isinstance(results, dict):
                entity = create_entity(results, fn_opts)
                if fn_opts.get('many'):
                    return [entity] if entity else []
                else:
                    return entity
            elif isinstance(results, basestring):
                entity = results
            else:
                raise NotImplementedError(
                    "Wrong output for method %s.%s: %s" % (name, func, results))

        for fn_name, method in methods.items():
            func = types.MethodType(functools.partial(method_fn, fn_opts=method), self)
            setattr(self, fn_name, func)

    def findall(self, **kwargs):
        for obj in self.list():
            found = True
            for attr_name, attr_val in kwargs.items():
                found = found and getattr(obj, attr_name) == attr_val
                if not found:
                    break
            if found:
                yield obj

    def get(self, user_id):
        try:
            return next(self.findall(id=user_id))
        except StopIteration:
            return None
