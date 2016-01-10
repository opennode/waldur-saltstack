import factory
from rest_framework.reverse import reverse

from nodeconductor.core.models import SynchronizationStates
from nodeconductor.structure.models import ServiceSettings
from nodeconductor.structure.tests.factories import CustomerFactory, ProjectFactory
from nodeconductor_saltstack.exchange.models import User, ExchangeTenant
from nodeconductor_saltstack.saltstack.models import SaltStackService, SaltStackServiceProjectLink


class ServiceSettingsFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = ServiceSettings

    name = factory.Sequence(lambda n: 'SaltStack settings %s' % n)
    state = SynchronizationStates.IN_SYNC
    shared = False
    type = 'SaltStack'


class ServiceFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = SaltStackService

    name = factory.Sequence(lambda n: 'SaltStack service %s' % n)
    settings = factory.SubFactory(ServiceSettingsFactory)
    customer = factory.SubFactory(CustomerFactory)


class ServiceProjectLinkFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = SaltStackServiceProjectLink

    service = factory.SubFactory(ServiceFactory)
    project = factory.SubFactory(ProjectFactory)
    state = SynchronizationStates.IN_SYNC


class ExchangeTenantFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = ExchangeTenant

    service_project_link = factory.SubFactory(ServiceProjectLinkFactory)
    domain = factory.Sequence(lambda n: 'domain-%s' % n)
    max_users = 10
    mailbox_size = 100
    state = ExchangeTenant.States.ONLINE

    @classmethod
    def get_url(cls, tenant=None, action=None):
        if tenant is None:
            tenant = ExchangeTenantFactory()
        url = reverse('exchange-tenants-detail', kwargs={'uuid': tenant.uuid})
        return url if action is None else url + action + '/'


class ExchangeUserFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = User

    tenant = factory.SubFactory(ExchangeTenantFactory)
    name = factory.Sequence(lambda n: 'user-%s' % n)
    backend_id = factory.Sequence(lambda n: 'backend_id-%s' % n)
    first_name = 'Alice'
    last_name = 'Lebowski'
    password = 'secret'
    mailbox_size = 100

    @classmethod
    def get_url(cls, user=None):
        if user is None:
            user = ExchangeUserFactory()
        return reverse('exchange-users-detail', kwargs={'uuid': user.uuid})
