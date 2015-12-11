from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import SharepointTenant


admin.site.register(SharepointTenant, structure_admin.ResourceAdmin)
