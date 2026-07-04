from django.contrib import admin

from .models import Assay, AssayTraceability, SampleAssay

@admin.register(Assay)
class AssayAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'methodology', 'normative_reference')
    search_fields = ('name', 'category', 'methodology')
    list_filter = ('category', 'methodology', 'is_active')
    readonly_fields = ('is_active',)

@admin.register(AssayTraceability)
class AssayTraceabilityAdmin(admin.ModelAdmin):
    list_display = ('assay', 'user_responsible', 'event', 'event_date')
    search_fields = ('assay__name', 'user_responsible__username', 'event')
    list_filter = ('event_date',)
    readonly_fields = ('assay', 'user_responsible', 'event', 'event_date')
    
@admin.register(SampleAssay)
class SampleAssayAdmin(admin.ModelAdmin):
    list_display = ('sample', 'assay', 'specification', 'units')
    search_fields = ('sample__name', 'sample__code', 'assay__name')
    list_filter = ('sample__name',)
    readonly_fields = ('sample', 'assay', 'specification', 'units')
    