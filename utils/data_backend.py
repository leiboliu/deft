import os
from django.conf import settings

from backend.models import DataFile


def convert_tags_to_html(content, tags):
    # input raw content and tags array/list
    # tag array ordered by start_index
    if len(tags) == 0:
        return content
    offset = 0
    # entity_text_template = '<span class="anno-entity" style="border-color: {};"><span ' \
    #                        'class="anno-words" style="color: {};">{}</span><span class="anno-ner" ' \
    #                        'style="background-color: {};">{}</span></span>'
    entity_text_template = '<span title="tagged by {}" class="anno-entity" style="border-color: {};"><span ' \
                           'class="anno-words" style="color: {};">{}</span><span class="anno-ner" ' \
                           'style="background-color: {};">{}</span></span>'
    for entity in tags:
        text_before = content[:(entity.start_index + offset)]
        text = content[(entity.start_index + offset):(entity.end_index + offset)]
        text_after = content[(entity.end_index + offset):]

        # if text != entity.text:
        #     continue
        entity_text = entity_text_template.format(
            entity.annotator if 'model' not in entity.annotator else 'model',
            entity.tag.colour, entity.tag.colour,
            text, entity.tag.colour, entity.tag.name)
        content = text_before + entity_text + text_after
        offset += (len(entity_text) - len(text))

    # print(content)
    return content


def convert_wip_to_output(wip_file, out_file):
    _ = wip_file, out_file
    pass


class LocalFileSystemBackend:
    ROOT_DIR = settings.BASE_DIR / "local_data"
    INPUT_SUBDIR = 'input'
    WIP_SUBDIR = 'wip'
    OUTPUT_SUBDIR = 'output'
    MODEL_SUBDIR = 'model'

    FILE_TYPE_PATH_MAPPING = {
        'input': (INPUT_SUBDIR, ''),
        'wip': (WIP_SUBDIR, '.html'),
        'output': (OUTPUT_SUBDIR, '.xml')
    }

    def __init__(self):
        if not os.path.exists(self.ROOT_DIR):
            os.mkdir(self.ROOT_DIR, 0o770)

    def _get_file_path(self, data_file, dest_file_type):
        return os.path.join(
            data_file.dataset.data_dir,
            self.FILE_TYPE_PATH_MAPPING[dest_file_type][0],
            data_file.name + self.FILE_TYPE_PATH_MAPPING[dest_file_type][1]
        )

    def create_project_dir(self, project):
        if not project.top_dir:
            project.top_dir = os.path.join(
                self.ROOT_DIR, project.title.lower().replace(' ', '_'))
            project.save(update_fields=["top_dir"])
        if not os.path.exists(project.top_dir):
            print('creating dirs')
            os.mkdir(project.top_dir, 0o770)
        if not os.path.exists(os.path.join(project.top_dir, self.MODEL_SUBDIR)):
            os.mkdir(os.path.join(project.top_dir, self.MODEL_SUBDIR), 0o770)

    def create_dataset_dirs(self, project, ds_list=None):
        if not project.top_dir:
            self.create_project_dir(project)

        if not ds_list:
            ds_list = project.datasets.all()

        for ds in ds_list:
            if not ds.data_dir:
                ds.data_dir = os.path.join(
                    project.top_dir, ds.title.lower().replace(' ', '_')
                )
                ds.save(update_fields=["data_dir"])

            if not os.path.exists(ds.data_dir):
                os.mkdir(ds.data_dir, 0o770)

            # in_subdir = os.path.join(ds.data_dir, self.INPUT_SUBDIR)
            # wip_subdir = os.path.join(ds.data_dir, self.WIP_SUBDIR)
            # out_subdir = os.path.join(ds.data_dir, self.OUTPUT_SUBDIR)
            #
            # if not os.path.exists(in_subdir):
            #     os.mkdir(in_subdir, 0o770)
            # if not os.path.exists(wip_subdir):
            #     os.mkdir(wip_subdir, 0o770)
            # if not os.path.exists(out_subdir):
            #     os.mkdir(out_subdir, 0o770)

    def import_data_files(self, project, ds_list=None):
        _ = self

        if not ds_list:
            ds_list = project.datasets.all()

        for d in ds_list:
            if not d.data_dir:
                continue
            # for f in os.listdir(os.path.join(d.data_dir, 'input')):
            for f in os.listdir(os.path.join(d.data_dir)):
                if f.startswith('.'):
                    continue
                DataFile.objects.get_or_create(dataset=d, name=f)

    def open_file(self, data_file, f_type):
        open(self._get_file_path(data_file, f_type), "rb")

    def write_wip(self, data_file, html_content):
        with open(self._get_file_path(data_file, 'wip'), "wb", encoding="utf-8") as o_file:
            o_file.write(html_content)

    def write_output(self, data_file):
        with open(self._get_file_path(data_file, 'wip'), encoding="utf-8") as wip_file, \
                open(self._get_file_path(data_file, 'output')) as out_file:
            convert_wip_to_output(wip_file, out_file)

    def audit_project_dirs(self, project, fix=True):
        pass
