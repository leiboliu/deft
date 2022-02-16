from django.contrib import admin

# Register your models here.
from backend.forms import TagForm, DatasetForm
from backend.models import Project, DataSet, DataFile, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'colour']
    form = TagForm

#
# class AssignStaffInline(admin.StackedInline):
#     model = Assignment


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status']
    readonly_fields = ['top_dir', ]
    # inlines = [AssignStaffInline]


class DatasetAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'title', 'status', 'import_data', 'export_to_xml']
    list_filter = ['project']
    readonly_fields = ['data_dir', ]


class DataFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'dataset', 'name', 'status', 'export_to_xml']
    list_filter = ['dataset__project']
    readonly_fields = ['dataset', 'name']
    form = DatasetForm


admin.site.register(Project, ProjectAdmin)
admin.site.register(DataSet, DatasetAdmin)
admin.site.register(DataFile, DataFileAdmin)
admin.site.register(Tag, TagAdmin)

