from django.contrib import admin

# Register your models here.
from backend.forms import TagForm, DatasetForm
from backend.models import Project, DataSet, DataFile, Tag, PretrainedModel, TaggedEntity
from member.models import Assignment


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'colour']
    form = TagForm

class AssignMemberInline(admin.StackedInline):
    model = Assignment

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'top_dir']
    readonly_fields = []
    inlines = [AssignMemberInline]


class DatasetAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'title', 'status', 'type', 'import_data', 'export_to_xml', 'export_deid']
    list_filter = ['project']
    readonly_fields = ['data_dir', ]


class DataFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'dataset', 'name', 'status', 'export_to_xml', 'export_deid']
    list_filter = ['dataset__project']
    readonly_fields = ['dataset', 'name']
    form = DatasetForm

class PretrainedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'project', 'scores', 'status', 'training_datetime', 'training_data_size']
    list_filter = ['project']
    # readonly_fields = ['scores', 'training_datetime']

class TaggedEntityAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_index', 'end_index', 'text', 'tag', 'doc', 'annotator', 'tagging_datetime']
    list_filter = ['tag', 'doc', 'annotator']


admin.site.register(Project, ProjectAdmin)
admin.site.register(DataSet, DatasetAdmin)
admin.site.register(DataFile, DataFileAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(PretrainedModel, PretrainedModelAdmin)
admin.site.register(TaggedEntity, TaggedEntityAdmin)

