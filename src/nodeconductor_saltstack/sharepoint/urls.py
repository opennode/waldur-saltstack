from . import views


def register_in(router):
    router.register(r'sharepoint-tenants', views.SiteViewSet, base_name='sharepoint-tenants')
