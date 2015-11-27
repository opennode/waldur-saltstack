from . import views


def register_in(router):
    router.register(r'saltstack', views.SaltStackServiceViewSet, base_name='saltstack')
    router.register(r'saltstack-service-project-link', views.SaltStackServiceProjectLinkViewSet, base_name='saltstack-spl')
