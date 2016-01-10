from mock import patch

from rest_framework import status, test

from nodeconductor.structure.tests import factories as structure_factories
from nodeconductor_saltstack.exchange.tests.factories import ExchangeUserFactory, ExchangeTenantFactory


@patch('nodeconductor_saltstack.exchange.models.ExchangeTenant.get_backend')
class UserCrudTest(test.APITransactionTestCase):
    def setUp(self):
        self.admin = structure_factories.UserFactory(is_staff=True)
        self.client.force_authenticate(self.admin)

    def test_user_can_update_tenant_domain(self, get_backend):
        tenant = ExchangeTenantFactory(domain='domain1')
        tenant_url = ExchangeTenantFactory.get_url(tenant, action='domain')
        response = self.client.post(tenant_url, data={'domain': 'domain2'})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('domain2', response.data['domain'])

        get_backend().tenants.change.assert_called_with(domain='domain2')

    def test_user_can_update_password(self, get_backend):
        exchange_user = ExchangeUserFactory(password='password1')
        user_url = ExchangeUserFactory.get_url(exchange_user)
        response = self.client.patch(user_url, data={'password': 'password2'})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('password2', response.data['password'])

        self.assertTrue(get_backend().users.change.called)
        get_backend().users.change_password.assert_called_once_with(
            id=exchange_user.backend_id,
            password='password2'
        )
