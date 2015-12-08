from nodeconductor.structure import views as structure_views
from . import models, serializers


class SiteViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Site.objects.all()
    serializer_class = serializers.SiteSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            domain=serializer.validated_data.get('domain'),
            storage_size=serializer.validated_data.get('storage_size'))
