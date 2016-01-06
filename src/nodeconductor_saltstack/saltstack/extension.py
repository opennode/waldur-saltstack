from nodeconductor.core import NodeConductorExtension


class SaltStackExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_saltstack.saltstack'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def celery_tasks():
        from datetime import timedelta
        return {
            'saltstack-sync-quotas': {
                'task': 'nodeconductor.saltstack.sync_quotas',
                'schedule': timedelta(hours=1),
                'args': ()
            },
        }
