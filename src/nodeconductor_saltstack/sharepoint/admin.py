from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import Site


admin.site.register(Site, structure_admin.ResourceAdmin)
