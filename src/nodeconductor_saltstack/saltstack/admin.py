from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import SaltStackServiceProjectLink, SaltStackService


admin.site.register(SaltStackService, structure_admin.ServiceAdmin)
admin.site.register(SaltStackServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
