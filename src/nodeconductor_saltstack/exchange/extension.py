from nodeconductor.core import NodeConductorExtension


class ExchangeExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_saltstack.exchange'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def celery_tasks():
        from datetime import timedelta
        return {
            'exchange-sync-tenants': {
                'task': 'nodeconductor.exchange.sync_tenants',
                'schedule': timedelta(minutes=60),
                'args': ()
            },
        }
