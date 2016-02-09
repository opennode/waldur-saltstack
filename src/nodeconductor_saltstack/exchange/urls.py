from . import views


def register_in(router):
    router.register(r'exchange-tenants', views.TenantViewSet, base_name='exchange-tenants')
    router.register(r'exchange-contacts', views.ContactViewSet, base_name='exchange-contacts')
    router.register(r'exchange-groups', views.GroupViewSet, base_name='exchange-groups')
    router.register(r'exchange-users', views.UserViewSet, base_name='exchange-users')
    router.register(r'exchange-conference-rooms', views.ConferenceRoomViewSet, base_name='exchange-conference-rooms')
