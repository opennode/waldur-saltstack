from django import forms

from rest_framework import serializers

from nodeconductor.template.forms import ResourceTemplateForm
from nodeconductor.template.serializers import BaseResourceTemplateSerializer
from nodeconductor_saltstack.exchange import models


class TenantProvisionTemplateForm(ResourceTemplateForm):
    domain = forms.CharField(required=False)
    max_users = forms.IntegerField(required=False)
    mailbox_size = forms.IntegerField(required=False)

    class Meta(ResourceTemplateForm.Meta):
        fields = ResourceTemplateForm.Meta.fields + ('domain', 'max_users', 'mailbox_size')

    class Serializer(BaseResourceTemplateSerializer):
        domain = serializers.CharField(required=False)
        max_users = serializers.IntegerField(required=False)
        mailbox_size = serializers.IntegerField(required=False)

    @classmethod
    def get_serializer_class(cls):
        return cls.Serializer

    @classmethod
    def get_model(cls):
        return models.ExchangeTenant
