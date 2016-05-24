from nodeconductor.core import NodeConductorExtension


class SharepointExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_saltstack.sharepoint'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def celery_tasks():
        from datetime import timedelta
        return {
            'sharepoint-sync-tenants': {
                'task': 'nodeconductor.sharepoint.sync_tenants',
                'schedule': timedelta(minutes=10),
                'args': ()
            },
        }
