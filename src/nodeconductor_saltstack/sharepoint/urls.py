from . import views


def register_in(router):
    router.register(r'sharepoint-sites', views.SiteViewSet, base_name='sharepoint-sites')
