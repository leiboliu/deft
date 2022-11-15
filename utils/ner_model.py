import math
import os
import random
import shutil
import time
from datetime import datetime
from threading import Thread

import torch
from flair.data import Sentence, Corpus
from flair.datasets import ColumnCorpus
from flair.models import SequenceTagger
from flair.embeddings import TransformerWordEmbeddings
from flair.trainers import ModelTrainer
# from torch.optim.lr_scheduler import OneCycleLR
from django.conf import settings
from backend.models import Project, DataFile, PretrainedModel, TaggedEntity

import spacy


class NERModel:
    def __init__(self, project, model_name):
        project = Project.objects.get(id=project)
        model_dir = project.top_dir + "/model/"

        ner_models = settings.CACHED_MODELS

        # check if project model has been initialized
        if ner_models.get(str(project.id)):
            self.tagger = ner_models.get(str(project.id))
        else:
            self.tagger = SequenceTagger.load(model_dir + model_name)
            ner_models[str(project.id)] = self.tagger

    def predict(self, text_content):
        entities = []
        # tokenizer = SpacyTokenizer('en_core_lg')
        sentence = Sentence(text_content)  # , use_tokenizer=tokenizer)
        self.tagger.predict(sentence)

        for entity in sentence.get_spans('ner'):
            entities.append({
                'start_index': entity.start_pos,
                'end_index': entity.end_pos,
                'tag': entity.tag,
                'text': text_content[entity.start_pos: entity.end_pos]
            })

        return entities


# model = NERModel("../local_data/project1/model/model.1.20220218.pt")
#
# with open("C:/Users/z5250377/PycharmProjects/deft/local_data/project1/dataset1/1 (1).txt", "r") as f:
#     text = f.read()
#     model.predict(text)

def split_train_val_test(datafiles):
    # 80 train 10 val 10 test
    ratios = settings.MODEL_TRAINING_DATA_RATIOS
    ratios = ratios.split(':')
    random.shuffle(datafiles)
    train_num = math.ceil(len(datafiles) * float(ratios[0]))
    train = datafiles[:train_num]
    val_num = math.ceil(len(datafiles) * float(ratios[1]))
    val = datafiles[train_num:(val_num + train_num)]
    test = datafiles[(val_num + train_num):]

    return train, val, test


class NERModelTrainer(Thread):
    def run(self) -> None:
        while True:
            # get the completed annotated documents for projects.
            # if number is divisible by [CONFIG: model retraining doc num: 100 currently]
            # for loop for projects
            print(self.ident)
            projects = Project.objects.all()
            for project in projects:
                datafiles = DataFile.objects.filter(dataset__project_id=project.id, status='C')
                # datafiles_ids = [file.id for file in datafiles]
                # datafile_status_completed = DocumentStatus.objects.filter(doc_id__in=datafiles_ids, status='C',
                #                                                           annotator='1')

                pretrained_model = PretrainedModel.objects.filter(project_id=project.id).order_by(
                    '-training_data_size').first()
                last_training_data_size = 0
                if pretrained_model is not None:
                    last_training_data_size = pretrained_model.training_data_size

                if len(datafiles) > 0 and \
                        (len(datafiles) - last_training_data_size) >= settings.MODEL_RETRAIN_THRESHOLD:
                    training_data = []

                    for file in datafiles:
                        text_entities = TaggedEntity.objects.filter(doc_id=file.id)
                        with open(text_entities[0].doc.get_path(), 'r', encoding="utf-8") as f:
                            text = f.read()

                        entities = []
                        for entity in text_entities:
                            entities.append((entity.start_index, entity.end_index, entity.tag.name))

                        training_data.append((text, entities))

                    # split
                    train, val, test = split_train_val_test(training_data)
                    # train model: training process data is saved to project_topdir/model/training_[currentdate]
                    now = datetime.now().strftime('%Y%m%d%H%M%S')
                    data_file_path = project.top_dir + '/model/train_' + now
                    os.makedirs(data_file_path, 0o755, True)
                    convert_to_bio_file(train, data_file_path + '/train.bio')
                    convert_to_bio_file(val, data_file_path + '/val.bio')
                    convert_to_bio_file(test, data_file_path + '/test.bio')

                    # start training
                    columns = {0: 'text', 1: 'ner'}
                    corpus: Corpus = ColumnCorpus(data_file_path, columns,
                                                  train_file='train.bio',
                                                  test_file='test.bio',
                                                  dev_file='val.bio')
                    tag_dictionary = corpus.make_tag_dictionary(tag_type='ner')

                    embeddings = TransformerWordEmbeddings('./pretrained/')

                    tagger = SequenceTagger(
                        hidden_size=256,
                        dropout=0.5,
                        embeddings=embeddings,
                        tag_dictionary=tag_dictionary,
                        tag_type='ner',
                        use_crf=True,
                        use_rnn=True,
                    )

                    trainer = ModelTrainer(tagger, corpus)

                    scores = trainer.train(data_file_path,
                                           learning_rate=0.1,
                                           mini_batch_size=2,
                                           max_epochs=10,
                                           )
                    final_score = scores['test_score']

                    # copy the final best-model to model folder with the name model.[project_id].date
                    if os.path.exists(data_file_path + '/best-model.pt'):
                        model_name = 'model.' + str(project.id) + '.' + now + '.pt'
                        target_file = project.top_dir + '/model/' + model_name
                        shutil.copyfile(data_file_path + '/best-model.pt', target_file)

                        # Save model to project_topdir/model folder and PretrainedModel object
                        try:
                            current_model = PretrainedModel.objects.get(project_id=project.id, status='C')
                            current_best_score = float(current_model.scores)
                            if final_score > current_best_score:
                                new_model = PretrainedModel(project_id=project.id, name=model_name, status='C',
                                                            scores=str(final_score),
                                                            training_data_size=len(datafiles))
                                new_model.save()
                                current_model.status = 'S'
                                current_model.save()

                                # reload the current model to CACHED_MODELS
                                new_tagger = SequenceTagger.load(target_file)
                                settings.CACHED_MODELS[str(project.id)] = new_tagger
                            else:
                                new_model = PretrainedModel(project_id=project.id, name=model_name, status='S',
                                                            scores=str(final_score),
                                                            training_data_size=len(datafiles))
                                new_model.save()
                        except PretrainedModel.DoesNotExist:
                            new_model = PretrainedModel(project_id=project.id, name=model_name, status='C',
                                                        scores=str(final_score),
                                                        training_data_size=len(datafiles))
                            new_model.save()
                            new_tagger = SequenceTagger.load(target_file)
                            settings.CACHED_MODELS[str(project.id)] = new_tagger

            time.sleep(settings.RETRAINING_CHECK_INTERVAL)


def convert_to_bio_file(data, output_file):
    # data is a list of text-entities tuple
    # data format: [(text, [(start, end, entity_tag), (), ...]), (text, [])....]
    # return: bio-format file based on the list [[(token1, ner_tag), (token2, ner_tag), ()], [],...]
    document = []
    nlp = spacy.load('en_core_web_sm')
    TAG_BEGIN = 'TAGTAGBEGIN'
    TAG_END = 'TAGTAGEND'

    for record_txt, record_entities in data:
        # insert Tag into the start/end positions
        offset = [0]
        for start, end, entity_tag in record_entities:
            start_idx = start + sum(offset)
            end_idx = end + sum(offset)
            offset.append(len(TAG_BEGIN) + len(TAG_END) + len(entity_tag) + 4)
            record_txt = record_txt[:start_idx] + ' ' + TAG_BEGIN + entity_tag + ' ' \
                         + record_txt[start_idx:end_idx] + ' ' + TAG_END + ' ' + record_txt[end_idx:]

        # remove the \r\n at the end of text.
        record_txt = record_txt.replace('\n', '')

        doc = nlp(record_txt)
        tokens = []
        tokens_bio = []
        entity_begin_flag = False
        entity_middle_flag = False
        entity_type = ''
        entity_token_index = 0
        same_type_entity_together = False
        previous_entity_type = ''

        for token in doc:
            if len(token.text.strip()) == 0:
                continue
            if token.text.startswith(TAG_BEGIN):
                entity_begin_flag = True
                entity_type = token.text[11:]
                if previous_entity_type != '' and previous_entity_type == entity_type:
                    same_type_entity_together = True
                continue

            if token.text.startswith(TAG_END):
                entity_begin_flag = False
                entity_middle_flag = False
                entity_type = ''
                entity_token_index = 0
                continue

            if entity_begin_flag and (not entity_middle_flag):
                # tokens.append(token.text)
                entity_token_index += 1
                tokens_bio.append('B-' + entity_type)

                entity_middle_flag = True
                previous_entity_type = entity_type

            elif entity_begin_flag and entity_middle_flag:
                # tokens.append(token.text)
                tokens_bio.append('I-' + entity_type)
                entity_token_index += 1

            elif not entity_begin_flag:
                # tokens.append(token.text)
                previous_entity_type = ''
                same_type_entity_together = False
                tokens_bio.append('O')

            tokens.append(token.text)

        # print(tokens)
        # print(tokens_bio)
        if len(tokens) != len(tokens_bio):
            raise Exception('Token length and BIO tag length are not the same.')

        document.append(list(zip(tokens, tokens_bio)))

    # write to file
    with open(output_file, 'w', encoding="utf-8", newline='\n') as f:
        for sent in document:
            for token, ner_tag in sent:
                f.write(token + ' ' + ner_tag + '\n')
            f.write('\n')
