from django.contrib import admin

from .models import Census

from import_export import resources
from import_export.admin import ImportExportModelAdmin

class CensusResource(resources.ModelResource):
    class Meta:
        model = Census

class CensusAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('name', 'voting_id')
    list_filter = ('name', 'voting_id')

    resource_class = CensusResource
    search_fields = ('voter_id', )




admin.site.register(Census, CensusAdmin)
