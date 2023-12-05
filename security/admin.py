from django.contrib import admin

from .models import Venue, Employee, Shift, Provider, Fee, Service, Invoice

# Register your models here.


class VenueAdmin(admin.ModelAdmin):
    filter_horizontal = ("users",)


class SeasonAdmin(admin.ModelAdmin):
    filter_horizontal = ("venues",)


class ShiftAdmin(admin.ModelAdmin):
    filter_horizontal = ("employees",)


class ProviderAdmin(admin.ModelAdmin):
    filter_horizontal = ("services",)


class InvoiceAdmin(admin.ModelAdmin):
    filter_horizontal = ("shifts",)


admin.site.register(Venue, VenueAdmin)
admin.site.register(Employee)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Fee)
admin.site.register(Service)
admin.site.register(Invoice, InvoiceAdmin)
