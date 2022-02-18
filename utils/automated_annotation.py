from backend.models import TaggedEntity, PretrainedModel, DataFile
from utils.ner_model import NERModel


def auto_annotate(project_id, doc_id, file_content):
    # step 1: check if the file has been predicted before
    # get current model name
    tags_by_model = []

    curent_model = PretrainedModel.objects.filter(project__id=project_id, status='C')
    if len(curent_model) == 0:
        return tags_by_model
    else:
        tags_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=curent_model.name).order_by('start_index')
        if len(tags_by_model) == 0:
            # step 2: If no, predict and insert TaggedEntity by model
            # predict
            ner_model = NERModel(curent_model.name)
            entities = ner_model.predict(file_content)
            doc = DataFile.objects.get(id=doc_id)
            # insert into tables
            for entity in entities:
                entity['annotator'] = curent_model.name
                entity['doc'] = doc
                entity_obj = TaggedEntity(**entity)
                entity_obj.save()

            # retrieve the tags again.
            tags_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=curent_model.name).order_by(
                'start_index')

    return tags_by_model
