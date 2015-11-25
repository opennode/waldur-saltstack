from . import views


def register_in(router):
    router.register(r'saltstack-sites', views.SiteViewSet, base_name='saltstack-sites')
