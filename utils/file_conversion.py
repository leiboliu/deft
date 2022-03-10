import os
from xml.dom import minidom

from bs4 import BeautifulSoup
from pathlib import Path

from lxml import etree

from backend.models import TaggedEntity
import xml.etree.ElementTree as ET

CONTENT_DIV_ID = 'content-div'
ANNO_ENTITY_CLASS = 'anno-entity'
ANNO_NER_CLASS = 'anno-ner'
ANNO_WORDS_CLASS = 'anno-words'


def _get_tags(wip_content):
    soup = BeautifulSoup(wip_content, 'html.parser')

    tag_list = []
    for ent in soup.find_all(name='span', class_=ANNO_ENTITY_CLASS):
        tag_list.append((
            ent.find(name='span', class_=ANNO_WORDS_CLASS).text,
            ent.find(name='span', class_=ANNO_NER_CLASS).text
        ))

    soup_div = soup

    while t := soup_div.find(name='span', class_=ANNO_NER_CLASS):
        t.decompose()

    div_text = soup_div.text

    return div_text, tag_list


def _get_wip(data_file):
    with open(data_file.get_path(w=True), 'r') as f:
        doc = f.read()
    return doc


def _write_to_xml(wip_content, p=None):

    div_text, tag_list = _get_tags(wip_content)

    if not p:
        print('<text>\n' + div_text + '</text>\n\n')

        print('<tags>')

        for tag in tag_list:
            w_list = tag[0].split()
            if len(w_list) == 1:
                start_w = end_w = w_list[0]
            else:
                start_w = w_list[0]
                end_w = w_list[-1]
            print(f'<{tag[1]} start="{start_w}" end="{end_w}" text="{tag[0]}">')

        print('</tags>')

    else:
        with open(p, 'w') as f:
            f.write('<text>\n' + div_text + '</text>\n\n')
            f.write('<tags>\n')
            for tag in tag_list:
                w_list = tag[0].split()
                if len(w_list) == 1:
                    start_w = end_w = w_list[0]
                else:
                    start_w = w_list[0]
                    end_w = w_list[-1]
                f.write(f'<{tag[1]} start="{start_w}" end="{end_w}" text="{tag[0]}">\n')

            f.write('</tags>')

def CDATA(text=None):
    element = ET.Element('![CDATA[')
    element.text = text
    return element

def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem

def _write_to_xml_v2(text, text_entities, output_file):
    data = etree.Element('deiddeft')
    text_element = etree.SubElement(data, 'text')
    text_element.text = etree.CDATA(text)
    tag_element = etree.SubElement(data, 'tags')
    for entity in text_entities:
        entity_element = etree.SubElement(tag_element, entity.tag.name)
        entity_element.set('start', str(entity.start_index))
        entity_element.set('end', str(entity.end_index))
        entity_element.set('text', entity.text)
        entity_element.set('type', entity.tag.name)

    xml_content = etree.tostring(data, method='xml', encoding='UTF-8',
                                 pretty_print=True, xml_declaration=True)
    with open(output_file, 'wb') as f:
        f.write(xml_content)



def write_results(data_file):
    # input DataFile obj
    with open(data_file.get_path(), 'r') as f:
        text = f.read()

    work_path = Path(data_file.get_path()).parent / 'export/'

    if not work_path.exists():
        work_path.mkdir(parents=True)

    output_file = Path(data_file.get_path()).stem + '.xml'
    output_file = work_path / output_file
    text_entities = TaggedEntity.objects.filter(doc_id=data_file.id, annotator='leibo')
    _write_to_xml_v2(text, text_entities, output_file)


def _write_deid_to_text(content, text_entities, output_file):
    if len(text_entities) == 0:
        return content
    offset = 0
    entity_text_template = '<**{}**>'

    for entity in text_entities:
        text_before = content[:(entity.start_index + offset)]
        text = content[(entity.start_index + offset):(entity.end_index + offset)]
        text_after = content[(entity.end_index + offset):]

        # if text != entity.text:
        #     continue
        entity_text = entity_text_template.format(entity.tag.name)
        content = text_before + entity_text + text_after
        offset += (len(entity_text) - len(text))

    # print(content)

    with open(output_file, 'w') as f:
        f.write(content)

def export_deid_text(data_file):
    # input DataFile obj
    with open(data_file.get_path(), 'r') as f:
        text = f.read()
    work_path = Path(data_file.get_path()).parent / 'export/de-identified/'

    if not work_path.exists():
        work_path.mkdir(parents=True)
    output_file = Path(data_file.get_path()).name
    output_file = work_path / output_file
    text_entities = TaggedEntity.objects.filter(doc_id=data_file.id, annotator='leibo')
    _write_deid_to_text(text, text_entities, output_file)

