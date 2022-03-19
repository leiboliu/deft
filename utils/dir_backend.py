
import os
from django.conf import settings


class LocalSystemDirs:

    ROOT_DIR = settings.BASE_DIR / "local_data"
    INPUT_SUBDIR = 'input'
    WIP_SUBDIR = 'wip'
    OUTPUT_SUBDIR = 'export'
    MODEL_SUBDIR = 'model'

    FILE_TYPE_PATH_MAPPING = {
        'input': (INPUT_SUBDIR, ''),
        'wip': (WIP_SUBDIR, '.html'),
        'output': (OUTPUT_SUBDIR, '.xml')
    }

    def __init__(self):
        if not os.path.exists(self.ROOT_DIR):
            os.mkdir(self.ROOT_DIR, 0o770)

    def create_project_dir(self, project):
        if not project.top_dir:
            project.top_dir = os.path.join(
                self.ROOT_DIR, project.title.lower().replace(' ', '_'))
            project.save(update_fields=["top_dir"])

        print(project.top_dir)

        if not os.path.exists(project.top_dir):
            print('creating dirs')
            os.mkdir(project.top_dir, 0o770)
            os.mkdir(os.path.join(project.top_dir, self.MODEL_SUBDIR), 0o770)
            # os.mkdir(os.path.join(project.top_dir, self.OUTPUT_SUBDIR), 0o770)

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
