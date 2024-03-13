from django.contrib import admin

from .models import Cliente, Datos_Revision

# Register your models here.



class platosView(admin.ModelAdmin):
    filter_horizontal = ("platos",)


admin.site.register(Cliente)
admin.site.register(Datos_Revision)
