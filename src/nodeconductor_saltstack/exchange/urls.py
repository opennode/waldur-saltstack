from . import views


def register_in(router):
    router.register(r'saltstack-tenants', views.TenantViewSet, base_name='saltstack-tenants')
    router.register(r'saltstack-tenants/(?P<tenant_uuid>[\w]+)/users', views.TenantUserViewSet, base_name='saltstack-tenantusers')
