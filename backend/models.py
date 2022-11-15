from django.db import models

# Create your models here.
from django.utils.safestring import mark_safe
import os
from utils.dir_backend import LocalSystemDirs
from django.utils import timezone
import os
from django.core.exceptions import ValidationError

class Tag(models.Model):
    name = models.CharField(max_length=64, null=False, unique=True, blank=False)
    colour = models.CharField(max_length=64, null=False, blank=False)

    class Meta:
        verbose_name_plural = ' Tags'

    def to_display(self):
        b = mark_safe(
            f'''<button class="btn btn-md thin-border anno-btn-raised anno-shadow" type="button"
            id="{self.name}"
            style="border-color: {self.colour}; color: white; background-color: {self.colour};"
            onclick="set_colour('{self.colour}', '{self.name}')"
            >{self.name}</button>'''
        )

        return b

    def to_tuple(self):
        mt = (self.name, self.colour)
        return mt

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


# class ProjectStatus(models.Model):
#     PROJECT_STATUS = [
#         ('ND', 'No Data Imported'),
#         ('DC', 'Directories Created'),
#         ('DA', 'Datasets Imported'),
#         ('C', 'Completed'),
#     ]
#     project_id = models.IntegerField()
#     status = models.CharField(max_length=3, choices=PROJECT_STATUS, default='NA')
#     annotator = models.IntegerField()  # refer to user id
#
#     def to_list(self):
#         return {
#             "id": self.id,
#             "project_id": self.project_id,
#             "annotator": self.annotator,
#             "status": self.get_status_display(),
#             "status_code": self.status
#         }


class Project(models.Model):
    def validate_dir(project_dir):
        if not os.path.isdir(project_dir):
            raise ValidationError('Invalid project dir')
        return project_dir

    PROJECT_STATUS = [
        ('ND', 'No Data Imported'),
        ('DC', 'Directories Created'),
        ('WIP', 'Work In Progress'),
        ('DA', 'Datasets Imported'),
        ('C', 'Completed'),
    ]

    title = models.CharField(max_length=256)
    top_dir = models.CharField(
        max_length=1024, unique=True, help_text="This is the path on the server. Example: 'H:/project/test/'",
        validators=[validate_dir]
    )
    status = models.CharField(
        max_length=4, default='DC', choices=PROJECT_STATUS
    )

    tags = models.ManyToManyField(Tag)

    class Meta:
        verbose_name_plural = '     Projects'

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        # if not self.top_dir:
        #     lb = LocalSystemDirs()
        #     lb.create_project_dir(self)

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title

    def ops(self):
        if self.status in ['ND', 'DC', 'DA']:
            return mark_safe(
                '<input type="button" id="import_'
                + str(self.id)
                + '" onclick="import_data('
                + str(self.id)
                + ')" value="Import Data">'
            )
        else:
            return ""

    def create_dirs(self):
        if self.status in ['ND', 'DC', 'DA']:
            return mark_safe(
                '<input type="button" id="create_'
                + str(self.id)
                + '" onclick="create_dirs('
                + str(self.id)
                + ')" value="Create Directories">'
            )
        else:
            return ""

    def to_list(self):
        return {
            "id": self.id,
            "name": self.title,
            "status": self.get_status_display(),
            "topdir": self.top_dir,
        }


# class DataSetStatus(models.Model):
#     DATASET_STATUS = [
#         ('ND', 'No Data Imported'),
#         ('DA', 'Datasets Imported'),
#         ('WIP', 'Work In Progress'),
#         ('C', 'Completed'),
#     ]
#     dataset_id = models.IntegerField()
#     status = models.CharField(max_length=3, choices=DATASET_STATUS, default='NA')
#     annotator = models.CharField(max_length=256)  # refer to username
#
#     def to_list(self):
#         return {
#             "id": self.id,
#             "dataset_id": self.dataset_id,
#             "annotator": self.annotator,
#             "status": self.get_status_display(),
#             "status_code": self.status
#         }


class DataSet(models.Model):
    DATASET_STATUS = [
        ('ND', 'No Data Imported'),
        ('DA', 'Datasets Imported'),
        ('WIP', 'Work In Progress'),
        ('C', 'Completed'),
    ]

    DATASET_TYPE = [
        ('ANNO', 'Annotation'),
        ('DEID', 'De-Identification'),
        ]

    project = models.ForeignKey(
        Project, related_name='datasets', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=256)
    data_dir = models.CharField(max_length=256, null=True, blank=True)
    status = models.CharField(
        max_length=4, default='ND', choices=DATASET_STATUS
    )
    type = models.CharField(
        max_length=4, default='DEID', choices=DATASET_TYPE
    )

    class Meta:
        verbose_name_plural = '    Datasets'

    def save(self, *args, **kwargs):
        super(DataSet, self).save(*args, **kwargs)
        if not self.data_dir:
            lb = LocalSystemDirs()
            lb.create_dataset_dirs(self.project, [self])
            # if self.project.status in ['ND', 'DC']:
            #     self.project.status = 'DC'
            #     self.project.save()

    def to_list(self):
        num_d, num_n, num_w, num_c = self.get_counts()

        return {
            "id": self.id,
            "name": self.title,
            "status": self.get_status_display(),
            "type": self.type,
            "num_total": num_d,
            "num_na": num_n,
            "num_wip": num_w,
            "num_complete": num_c
        }

    def get_counts(self):
        num_d = DataFile.objects.filter(dataset=self).count()
        num_n = DataFile.objects.filter(dataset=self).filter(status='NA').count()
        num_w = DataFile.objects.filter(dataset=self).filter(status='WIP').count()
        num_c = DataFile.objects.filter(dataset=self).filter(status='C').count()
        return num_d, num_n, num_w, num_c

    def import_data(self):
        return mark_safe(
            '<input type="button" id="import_'
            + str(self.id)
            + '" onclick="import_data('
            + str(self.project.id)
            + ','
            + str(self.id)
            + ')" value="Import Data"'
            + ('disabled>' if self.type=='DEID' else '>')
        )

    def export_to_xml(self):
        return mark_safe(
            f'''<input id="export_"{self.id}" type="button" onclick="export_data({self.id}, 'ds')" value="Export Dataset">''')

    def export_deid(self):
        return mark_safe(
            f'''<input id="export_"{self.id}" type="button" onclick="export_deid_data({self.id}, 'ds')" value="Export de-identified Data">''')

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title


# class DocumentStatus(models.Model):
#     FILE_STATUS = [
#         ('NA', 'Not Annotated'),
#         ('WIP', 'Work In Progress'),
#         ('C', 'Complete'),
#     ]
#     doc_id = models.IntegerField()
#     status = models.CharField(max_length=3, choices=FILE_STATUS, default='NA')
#     annotator = models.CharField(max_length=256)  # refer to username
#
#     def to_list(self):
#         return {
#             "id": self.id,
#             "doc_id": self.doc_id,
#             "annotator": self.annotator,
#             "status": self.get_status_display(),
#             "status_code": self.status
#         }


class DataFile(models.Model):
    FILE_STATUS = [
        ('NA', 'Not Annotated'),
        ('WIP', 'Work In Progress'),
        ('C', 'Complete'),
    ]

    dataset = models.ForeignKey(
        DataSet, related_name='files', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256)
    status = models.CharField(max_length=3, choices=FILE_STATUS, default='NA')

    class Meta:
        verbose_name_plural = '   Datafiles'

    def to_list(self):
        # b = mark_safe(
        #     f'<a href="{self.dataset.project_id}/{self.dataset_id}/{self.id}">{self.id}</a>')
        # name = mark_safe(
        #     f'<a href="{self.dataset.project_id}/{self.dataset_id}/{self.id}">{self.name}</a>')
        return {
            "id": self.id,
            "project_id": self.dataset.project_id,
            "dataset_id": self.dataset_id,
            "name": self.name,
            "status": self.get_status_display(),
            "status_code": self.status
        }

    def get_path(self, w=False):
        # only return raw content
        return os.path.join(self.dataset.data_dir, f'{self.name}')

        # if self.status == 'NA' and not w:
        #     return os.path.join(self.dataset.data_dir, f'input/{self.name}')
        # return os.path.join(self.dataset.data_dir, f'wip/{self.name}')

    def get_res_path(self):
        n = self.name.split('.')[0]
        return os.path.join(self.dataset.data_dir, f'output/{n}.xml')

    def export_to_xml(self):
        return mark_safe(
            f'''<input id="export_"{self.id}" type="button" onclick="export_data({self.id}, 'f')" value="Export file">''')

    def export_deid(self):
        return mark_safe(
            f'''<input id="export_"{self.id}" type="button" onclick="export_deid_data({self.id}, 'f')" value="Export de-identified Data">''')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class TaggedEntity(models.Model):
    doc = models.ForeignKey(DataFile, related_name='entities', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name='entity_tags', on_delete=models.CASCADE)
    text = models.CharField(max_length=256, null=True, blank=True)
    annotator = models.CharField(max_length=256)
    start_index = models.IntegerField()
    end_index = models.IntegerField()
    tagging_datetime = models.DateTimeField(editable=False)

    def to_list(self):
        return {
            "id": self.id,
            "entity": self.tag.name,
            "entity_color": self.tag.colour,
            "start": self.start_index,
            "end": self.end_index,
            "text": self.text,
            "annotator": self.annotator,
        }

    def save(self, *args, **kwargs):
        if not self.id:
            self.tagging_datetime = timezone.now()

        return super(TaggedEntity, self).save(*args, **kwargs)


class PretrainedModel(models.Model):
    FILE_STATUS = [
        ('C', 'Current Model'),
        ('S', 'Superseded'),
    ]
    # model: model.project_id.date_trained
    name = models.CharField(max_length=256, null=False, unique=True, blank=False)
    training_datetime = models.DateTimeField(editable=False)
    project = models.ForeignKey(Project, related_name='project_pretrained_model', on_delete=models.CASCADE)
    scores = models.CharField(max_length=256)
    status = models.CharField(max_length=3, choices=FILE_STATUS, default='C')
    training_data_size = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.training_datetime = timezone.now()

        return super(PretrainedModel, self).save(*args, **kwargs)
