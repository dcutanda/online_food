from django.contrib import admin
from . models import Vendor, OpeningHour


# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'is_approved', 'created_date')
    list_display_links = ('user', 'vendor_name')

class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'day', 'from_hour', 'to_hour')

admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)