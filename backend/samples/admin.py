from django.contrib import admin

from .models import SampleType, Sample, SampleTraceability


@admin.register(SampleType)
class SampleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'prefix', 'is_active')
    search_fields = ('name', 'prefix')
    list_filter = ('is_active',)


class SampleTraceabilityInline(admin.TabularInline):
    model = SampleTraceability
    extra = 0
    readonly_fields = ('user_responsible', 'event', 'event_date')
    can_delete = False


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'client', 'type', 'status', 'received_date', 'is_active')
    search_fields = ('code', 'name', 'client__name', 'description')
    list_filter = ('status', 'is_active', 'type', 'received_date')
    readonly_fields = ('code', 'name', 'client', 'type', 'status', 'received_date', 'is_active')
    inlines = [SampleTraceabilityInline]


@admin.register(SampleTraceability)
class SampleTraceabilityAdmin(admin.ModelAdmin):
    list_display = ('sample', 'user_responsible', 'event', 'event_date')
    search_fields = ('sample__code', 'sample__name', 'user_responsible__username', 'event')
    list_filter = ('event_date',)
    readonly_fields = ('sample', 'user_responsible', 'event', 'event_date')
    