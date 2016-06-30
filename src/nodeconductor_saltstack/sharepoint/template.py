from nodeconductor.template.forms import ResourceTemplateForm
from nodeconductor.template.serializers import BaseResourceTemplateSerializer
from nodeconductor_saltstack.sharepoint import models


class SharepointTenantTemplateForm(ResourceTemplateForm):

    class Meta(ResourceTemplateForm.Meta):
        fields = ResourceTemplateForm.Meta.fields

    class Serializer(BaseResourceTemplateSerializer):
        pass

    @classmethod
    def get_serializer_class(cls):
        return cls.Serializer

    @classmethod
    def get_model(cls):
        return models.SharepointTenant
