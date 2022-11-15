from backend.models import TaggedEntity, PretrainedModel, DataFile, Tag
from utils.ner_model import NERModel


def auto_annotate(project_id, doc_id, file_content):
    # step 1: check if the file has been predicted before
    # get current model name
    tags_by_model = []

    current_model = PretrainedModel.objects.filter(project__id=project_id, status='C')
    # model = PretrainedModel(name='model.4.20220219.pt', project_id=project_id, scores='99.05', status='C')
    # model.save()
    # current_model[0].name = 'model.4.20220219.pt'
    # current_model[0].save()


    if len(current_model) == 0:
        return tags_by_model
    else:
        current_model = current_model[0]
        tags_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=current_model.name).order_by('start_index')

        if len(tags_by_model) != 0:
            if tags_by_model[0].annotator != current_model.name:
                tags_by_model.delete()
            else:
                return tags_by_model

        # step 2: If no, predict and insert TaggedEntity by model
        # predict
        ner_model = NERModel(project_id, current_model.name)
        entities = ner_model.predict(file_content)
        doc = DataFile.objects.get(id=doc_id)
        # insert into tables
        for entity in entities:
            entity['annotator'] = current_model.name
            entity['doc'] = doc
            tag = Tag.objects.get(name=entity['tag'])
            entity['tag'] = tag
            entity_obj = TaggedEntity(**entity)
            entity_obj.text = ''
            entity_obj.save()

        # retrieve the tags again.
        tags_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=current_model.name).order_by(
            'start_index')
        for tag in tags_by_model:
            tag.text = file_content[tag.start_index:tag.end_index]

    return tags_by_model
