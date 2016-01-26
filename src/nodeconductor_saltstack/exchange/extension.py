from nodeconductor.core import NodeConductorExtension


class ExchangeExtension(NodeConductorExtension):

    class Settings:
        SMS_EMAIL_FROM = 'gcloud_zabbix@ita.gov.om'
        SMS_EMAIL_GATEWAY = '{phone}@esms.ita.gov.om'
        SMS_PHONE_REGEX = r'^9\d{7}$'

    @staticmethod
    def django_app():
        return 'nodeconductor_saltstack.exchange'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
