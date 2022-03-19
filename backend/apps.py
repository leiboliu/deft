import os
from django.apps import AppConfig
from django.conf import settings




class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'


    def ready(self):
        # django will load two env: one is main and one is reload. ready function will be called twice
        # so need to initialize CACHED_MODEL
        if os.environ.get('RUN_MAIN', None) == 'true': # this is for reload env. change == to != for non-reload env
            from backend.models import PretrainedModel
            from flair.models import SequenceTagger
            print("Initialization started")
            pretrained_models = PretrainedModel.objects.filter(status='C')
            for model in pretrained_models:
                project_id = model.project.id
                model_path = model.project.top_dir + '/model/' + model.name
                tagger = SequenceTagger.load(model_path)
                settings.CACHED_MODELS[str(project_id)] = tagger
                print("load model {} successfully for project {}".format(model.name, project_id))
                # predict all the NA files for this project
                from backend.models import DataSet, DataFile, TaggedEntity
                from utils.automated_annotation import auto_annotate
                datafiles_na = DataFile.objects.filter(status='NA', dataset__project_id=project_id)
                for file in datafiles_na:
                    entities = TaggedEntity.objects.filter(doc=file)
                    if len(entities) != 0 and (entities[0].annotator != model.name):
                        entities.delete()
                        entities = []

                    if len(entities) == 0:
                        with open(file.get_path(), 'r') as f:
                            doc_content = f.read()
                            auto_annotate(project_id, file.id, doc_content)

            print("Initialization done")



            if settings.AUTO_MODEL_RETRAINING:
                # start the model training thread
                from utils.ner_model import NERModelTrainer
                model_training_thread = NERModelTrainer(daemon=False)
                model_training_thread.start()
                print('Auto model retraining process startup')

            print('backend module startup')


