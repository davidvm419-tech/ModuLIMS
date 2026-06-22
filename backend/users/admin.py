from django.contrib import admin

from .models import User, UserTraceability

# Register your models here.

@admin.register(User)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'identification', 'email', 'username', 'job_title', 'rol', 'is_active')
    search_fields = ('first_name', 'last_name', 'identification')
    list_filter = ('is_active',)


class UserTraceabilityInline(admin.TabularInline):
    model = UserTraceability
    extra = 0
    readonly_fields = ('user_responsible', 'event', 'event_date')
    can_delete = False
