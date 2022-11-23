from django.contrib import admin

from .models import Census


class CensusAdmin(admin.ModelAdmin):
    list_display = ('name', 'voting_id')
    list_filter = ('name', 'voting_id')

    search_fields = ('voter_id', )




admin.site.register(Census, CensusAdmin)