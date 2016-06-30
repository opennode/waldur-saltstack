from . import views


def register_in(router):
    router.register(r'sharepoint-templates', views.TemplateViewSet, base_name='sharepoint-templates')
    router.register(r'sharepoint-tenants', views.TenantViewSet, base_name='sharepoint-tenants')
    router.register(r'sharepoint-users', views.UserViewSet, base_name='sharepoint-users')
    router.register(r'sharepoint-site-collections', views.SiteCollectionViewSet, base_name='sharepoint-site-collections')
