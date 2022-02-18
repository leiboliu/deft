from flair.data import Sentence
from flair.models import SequenceTagger


class NERModel:
    def __init__(self, model_path):
        self.tagger = SequenceTagger.load(model_path)

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

