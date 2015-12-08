from django import forms

from rest_framework import serializers

from nodeconductor.template.forms import TemplateForm
from nodeconductor.template.serializers import BaseTemplateSerializer
from nodeconductor_saltstack.exchange import models


class TenantProvisionTemplateForm(TemplateForm):
    domain = forms.CharField(required=False)
    max_users = forms.IntegerField(required=False)
    mailbox_size = forms.IntegerField(required=False)

    class Meta(TemplateForm.Meta):
        fields = TemplateForm.Meta.fields + ('domain', 'max_users', 'mailbox_size')

    class Serializer(BaseTemplateSerializer):
        domain = serializers.CharField(required=False)
        max_users = serializers.IntegerField(required=False)
        mailbox_size = serializers.IntegerField(required=False)

    @classmethod
    def get_serializer_class(cls):
        return cls.Serializer

    @classmethod
    def get_resource_model(cls):
        return models.Tenant
