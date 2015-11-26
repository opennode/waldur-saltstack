from nodeconductor.core import NodeConductorExtension


class ExchangeExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_saltstack.exchange'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
