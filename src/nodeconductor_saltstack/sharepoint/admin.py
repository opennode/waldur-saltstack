from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import SharepointTenant, Template, Site, User


admin.site.register(SharepointTenant, structure_admin.ResourceAdmin)

admin.site.register(Template)
admin.site.register(Site)
admin.site.register(User)
