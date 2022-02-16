
from bs4 import BeautifulSoup
import re


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


def _write_to_xml_v2(wip_content, output_path):

    re_entity_span = re.compile(
        r'<span\s+class="anno-entity".*?>'
        r'<span\s+class="anno-words".*?>(?P<words>.*?)</span>'
        r'<span\s+class="anno-ner".*?>(?P<tag>.*?)</span>'
        r'</span>')

    tags = []
    text_content = ''

    while m := re_entity_span.search(wip_content):
        print(
            f'{m.start()} to {m.start() + len(m.group("words"))} [{m.group("tag")}]: '
            f'{m.group("words")}'
        )
        tags.append([
            m.group('tag'),
            len(text_content) + m.start(),
            len(text_content) + m.start() + len(m.group('words')),
            m.group('words'),
        ])
        text_content += (wip_content[:m.start()] + m.group('words'))
        wip_content = wip_content[m.end():]

    text_content += wip_content

    if output_path:
        print(f'text:\n {text_content}\n')
        with open(output_path, 'w') as f:
            f.write(f'<text>\n{text_content}\n</text>\n')

            f.write('<tags>\n')
            for t in tags:
                print(t)
                f.write(
                    f'<{t[0]} start="{t[1]}" end="{t[2]}" '
                    f'words="{t[3]}" source="human">\n'
                )
            f.write('</tags>\n')


def write_results(data_file):
    wip_content = _get_wip(data_file)
    _write_to_xml_v2(wip_content, data_file.get_res_path())

