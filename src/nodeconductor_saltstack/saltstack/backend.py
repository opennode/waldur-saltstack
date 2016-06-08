import re
import json
import types
import logging
import requests
import functools

from django.utils import six
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models
from .. import __version__


logger = logging.getLogger(__name__)


def parse_size(size_str):
    """ Convert string notation of size to a number in MB """
    MAPPING = {
        'KB': lambda s: float(s) / 1024,
        'MB': lambda s: float(s),
        'GB': lambda s: int(ServiceBackend.gb2mb(float(s))),
    }

    size, unit = size_str.split()
    return MAPPING[unit](size)


class SaltStackBackendError(ServiceBackendError):

    def __init__(self, message, traceback=None):
        super(SaltStackBackendError, self).__init__(message)
        self.traceback = traceback
        self.traceback_str = 'Error'
        if isinstance(traceback, basestring):
            self.traceback_str = traceback
        elif isinstance(traceback, dict):
            self.traceback_str = '; '.join(["%s: %s" % (k, v) for k, v in traceback.items()])


class SaltStackBackend(object):

    backends = set()

    def __init__(self, settings, backend_class=None, **kwargs):
        if not backend_class:
            backend_class = SaltStackBaseBackend
        backends = list(self.backends) + [SaltStackBaseBackend]
        if backend_class not in backends:
            raise SaltStackBackendError("Unknown SaltStack backend class: %s" % backend_class)

        self.backend = backend_class(settings, **kwargs)

    def __getattr__(self, name):
        return getattr(self.backend, name)

    @classmethod
    def register(cls, backend_class):
        cls.backends.add(backend_class)


class SaltStackMetaclass(type):

    def __new__(cls, name, bases, args):
        new_class = super(SaltStackMetaclass, cls).__new__(cls, name, bases, args)
        if args['API']:
            SaltStackBackend.register(new_class)
        return new_class


class SaltStackBaseBackend(six.with_metaclass(SaltStackMetaclass, ServiceBackend)):

    TARGET_OPTION_NAME = NotImplemented
    MAPPING_OPTION_NAME = NotImplemented
    API = {}

    def __init__(self, settings, **kwargs):
        self.settings = settings

        options = settings.options or {}
        apis = dict(base=SaltStackBaseAPI, service_settings=ServiceSettingsAPI, **self.API)
        for name, api_cls in apis.items():
            try:
                api = api_cls(
                    settings.backend_url, settings.username, settings.password,
                    options.get(self.TARGET_OPTION_NAME, ''),
                    options.get(self.MAPPING_OPTION_NAME))
            except SaltStackBackendError:
                continue
            else:
                setattr(api, 'backend', self)
                setattr(self, name, api)

    def sync_backend(self):
        pass

    def sync(self):
        for cls in SaltStackBackend.backends:
            cls(self.settings).sync_backend()

    def ping(self, raise_exception=False):
        try:
            return all(cls(self.settings).base.ping() for cls in SaltStackBackend.backends)
        except Exception as e:
            if raise_exception:
                six.reraise(SaltStackBackendError, e)
            return False

    def get_stats(self):
        links = models.SaltStackServiceProjectLink.objects.filter(
            service__settings=self.settings)
        quota_names = ('exchange_storage', 'sharepoint_storage')
        quota_values = models.SaltStackServiceProjectLink.get_sum_of_quotas_as_dict(
            links, quota_names=quota_names, fields=['limit'])
        quota_stats = {
            'exchange_storage_quota': quota_values.get('exchange_storage', -1.0),
            'sharepoint_storage_quota': quota_values.get('sharepoint_storage', -1.0),
        }

        stats = {}
        for quota in self.settings.quotas.all():
            if quota.name not in quota_names:
                continue
            stats[quota.name] = quota.limit
            stats[quota.name + '_usage'] = quota.usage
        stats.update(quota_stats)
        return stats


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
                "Request to salt API %s failed: %s %s" % (url, response.status_code, response.text))

    def ping(self):
        response = self.request('/run', {
            'client': 'local',
            'fun': 'test.ping',
            'tgt': self.target,
        })

        return all(response['return'][0].values())

    def run_cmd(self, cmd, **kwargs):

        def prepare_args():
            for k, v in kwargs.iteritems():
                if v is None:
                    yield '-{}'.format(k)
                elif isinstance(v, bool):
                    yield '-{} {}'.format(k, str(v).lower())
                else:
                    if isinstance(v, basestring):
                        v = re.sub(r'(["\$])', r'\\\1', v)
                    yield '-{} "{}"'.format(k, v)

        command = self.COMMAND.format(name=self.MAPPING.get(cmd) or cmd, args=' '.join(prepare_args()))

        logger.debug('Executing command: {}'.format(command))

        response = self.request('/run', {
            'client': 'local',
            'fun': 'cmd.run',
            'tgt': self.target,
            'arg': command,
        })

        for tgt, res in response['return'][0].items():
            try:
                result = json.loads(res)
            except ValueError:
                logger.error("Cannot parse output of command %s: %s", command, res)
                raise SaltStackBackendError(
                    "Error during execution of %s on %s: %s" % (cmd, tgt, res))

            if result['Status'] != 'Inactive':
                break
        else:
            raise SaltStackBackendError(
                "Empty response from SaltStack during execution of %s on %s" % (cmd, self.target))

        if result['Status'] == 'OK':
            return result['Output']
        else:
            logger.error("Output from a failed call of command %s: %s" % (command, result.get('Output')))
            raise SaltStackBackendError(
                "Cannot run command %s on %s: %s" % (
                    cmd, self.target, result.get('Message') or result.get('Output')),
                result.get('Message'))


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
                        'manager': 'ManagerEmail',
                    },
                    paths={  # extracts input argumets from supplied objects
                        'manager': 'user.email',  # manager --> manager.user.email --> ManagerEmail
                    },
                    defaults={  # default parameters for input data
                        # if default is a function - it will receive backend and method kwargs as parameters
                        'tenant': lambda backend, **kwargs: backend.tenant.name,
                        # if default is a string - it will be formatted with method kwargs (.format(**kwargs))
                        'domain': '{tenant}',
                    },
                    output={  # output fields mapping
                        'Accepted DomainName': 'domain',
                        'DistinguishedName': 'dn',
                    },
                    # if output is specified as '*' - return task result without mapping.
                    clean={  # execute some operations on output before provision
                        'Accepted DomainName': <clean_function>
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

            # If output specified as * - return all
            if fn_opts.get('output') == '*':
                return entity

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
                            kwargs[opt] = fn.format(backend=self.backend, **kwargs)
                        elif isinstance(fn, types.FunctionType):
                            kwargs[opt] = fn(self.backend, **kwargs)
                        elif isinstance(fn, (int, bool, float)) or fn is None:
                            kwargs[opt] = fn
                        else:
                            raise NotImplementedError(
                                "Unknown default argument '%s' for method %s.%s" % (opt, name, func))

            paths = fn_opts.get('paths') or {}
            for opt, val in kwargs.items():
                if opt in inp:
                    if opt in paths:
                        opts[inp[opt]] = reduce(getattr, paths[opt].split('.'), val)
                    else:
                        opts[inp[opt]] = val
                else:
                    raise NotImplementedError(
                        "Unknown argument '%s' for method %s.%s" % (opt, name, func))

            results = self.run_cmd(func, **opts)

            if isinstance(results, list):
                entities = [create_entity(entity, fn_opts) for entity in results]
                if fn_opts.get('many'):
                    return entities
                elif len(entities) > 0:
                    return entities[0]
                else:
                    return []
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

    # methods findall() and get() expects list() method implementation
    def findall(self, **kwargs):
        for obj in self.list():
            found = True
            for attr_name, attr_val in kwargs.items():
                found = found and getattr(obj, attr_name) == attr_val
                if not found:
                    break
            if found:
                yield obj

    def get(self, obj_id):
        try:
            return next(self.findall(id=obj_id))
        except StopIteration:
            return None


class ServiceSettingsAPI(SaltStackBaseAPI):

    class Methods:
        get_storage = dict(
            name='DiskUsage',
            input={
                'drive': 'DriveLetter',
            },
            output={
                'Free [MB]': 'free',
                'Used [MB]': 'used',
            },
            defaults={
                'drive': 'D',
            },
            clean={
                'Free [MB]': int,
                'Used [MB]': int,
            }
        )
