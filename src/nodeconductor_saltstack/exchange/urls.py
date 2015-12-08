from . import views


def register_in(router):
    router.register(r'exchange-tenants', views.TenantViewSet, base_name='exchange-tenants')
    router.register(r'exchange-tenants/(?P<tenant_uuid>[\w]+)/contacts', views.ContactViewSet, base_name='exchange-contacts')
    router.register(r'exchange-tenants/(?P<tenant_uuid>[\w]+)/groups', views.GroupViewSet, base_name='exchange-groups')
    router.register(r'exchange-tenants/(?P<tenant_uuid>[\w]+)/users', views.UserViewSet, base_name='exchange-users')
