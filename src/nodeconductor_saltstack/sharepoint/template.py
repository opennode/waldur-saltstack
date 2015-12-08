from django import forms

from rest_framework import serializers

from nodeconductor.template.forms import TemplateForm
from nodeconductor.template.serializers import BaseTemplateSerializer
from nodeconductor_saltstack.sharepoint import models


class SiteProvisionTemplateForm(TemplateForm):

    class Meta(TemplateForm.Meta):
        fields = TemplateForm.Meta.fields

    class Serializer(BaseTemplateSerializer):
        pass

    @classmethod
    def get_serializer_class(cls):
        return cls.Serializer

    @classmethod
    def get_resource_model(cls):
        return models.Site
