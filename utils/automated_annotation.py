from backend.models import TaggedEntity, PretrainedModel, DataFile, Tag
from utils.ner_model import NERModel


def auto_annotate(project_id, doc_id, file_content):
    # step 1: check if the file has been predicted before
    # get current model name
    tags_by_model = []

    curent_model = PretrainedModel.objects.filter(project__id=project_id, status='C')
    # model = PretrainedModel(name='model.1.20220218', project_id=project_id, scores='99.05', status='C')
    # model.save()

    if len(curent_model) == 0:
        return tags_by_model
    else:
        curent_model = curent_model[0]
        tags_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=curent_model.name).order_by('start_index')
        if len(tags_by_model) == 0:
            # step 2: If no, predict and insert TaggedEntity by model
            # predict
            ner_model = NERModel(project_id, curent_model.name)
            entities = ner_model.predict(file_content)
            doc = DataFile.objects.get(id=doc_id)
            # insert into tables
            for entity in entities:
                entity['annotator'] = curent_model.name
                entity['doc'] = doc
                tag = Tag.objects.get(name=entity['tag'])
                entity['tag'] = tag
                entity_obj = TaggedEntity(**entity)
                entity_obj.save()

            # retrieve the tags again.
            tags_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=curent_model.name).order_by(
                'start_index')

    return tags_by_model
