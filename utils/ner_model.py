from flair.data import Sentence
from flair.models import SequenceTagger

from backend.models import Project
from deft.settings import ner_models, BASE_DIR


class NERModel:
    def __init__(self, project, model_name):
        project = Project.objects.get(id=project)
        model_dir = project.top_dir + "/model/"
        # check if project model has been initialized
        if ner_models.get(str(project)):
            self.tagger = ner_models.get(str(project))
        else:
            self.tagger = SequenceTagger.load(model_dir + model_name + ".pt")
            ner_models[str(project)] = self.tagger

    def predict(self, text_content):
        entities = []
        sentence = Sentence(text_content)
        self.tagger.predict(sentence)

        for entity in sentence.get_spans('ner'):
            entities.append({
                'start_index': entity.start_pos,
                'end_index': entity.end_pos,
                'tag': entity.tag,
                'text': entity.text
            })

        return entities

# model = NERModel("../local_data/project1/model/model.1.20220218.pt")
#
# with open("C:/Users/z5250377/PycharmProjects/deft/local_data/project1/dataset1/1 (1).txt", "r") as f:
#     text = f.read()
#     model.predict(text)



