from django.contrib import admin

from .models import Client
# Register your models here.

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'nit', 'address', 'contact_person', 'email', 'phone', 'is_active')
    search_fields = ('name', 'nit', 'contact_person')
    list_filter = ('is_active',)
    readonly_fields = ('name', 'nit', 'address', 'contact_person', 'email', 'phone', 'is_active')