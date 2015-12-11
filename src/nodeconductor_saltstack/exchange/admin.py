from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import ExchangeTenant


admin.site.register(ExchangeTenant, structure_admin.ResourceAdmin)
