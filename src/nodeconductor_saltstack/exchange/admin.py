from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import Tenant


admin.site.register(Tenant, structure_admin.ResourceAdmin)
