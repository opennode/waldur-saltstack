from nodeconductor.core import NodeConductorExtension


class SaltStackExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_saltstack.sharepoint'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
