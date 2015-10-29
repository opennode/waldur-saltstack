from . import views


def register_in(router):
    router.register(r'saltstack', views.SaltStackServiceViewSet, base_name='saltstack')
    router.register(r'saltstack-service-project-link', views.SaltStackServiceProjectLinkViewSet, base_name='saltstack-spl')
    router.register(r'saltstack-domains', views.DomainViewSet, base_name='saltstack-domains')
    router.register(r'saltstack-sites', views.SiteViewSet, base_name='saltstack-sites')
    router.register(r'saltstack-domains/(?P<domain_uuid>[\w]+)/users', views.DomainUserViewSet, base_name='saltstack-domainusers')
