import cProfile
import importlib
import json
from pprint import pprint

from tqdm import tqdm

from mwparserfromhell.parser import Parser as WikiParser

from wikitools import data_extractor
from wikitools import wiki_to_html

from wikitools import html_formatter
from wikitools import wiki_urls


db_file_path = 'data/dump-data.db'

def main_process(db_file_path: str = 'data/dump-data.db',
                 sample_size: int = 0,
                 pages_data: list = None,
                 steps: list = None):
    data_sizes = {
        'init': len(pages_data) if(pages_data) else 0,
    }
    if(steps is None):
        steps = [ 'load', 'parse', 'filter-language', 'translations', 'translation-templates' ]
    print(f'running steps: {steps}')
    if('load' in steps):
        print('loading...')
        pages_data = data_extractor.prepare_pages(db_file_path, skip_parsing=True, sample_size=sample_size)
        data_sizes['load'] = len(pages_data)
    if('parse' in steps):
        print('parsing...')
        pages_data = data_extractor.parse_pages_wiki(pages_data)
        data_sizes['parse'] = len(pages_data)
    english_pages = None
    german_pages = None
    if('filter-language' in steps):
        print('filtering for languages...')
        english_pages = data_extractor.filter_language(pages_data, language='English')
        german_pages = data_extractor.filter_language(pages_data, language='German')
    translations = None
    translation_texts = None
    if('translations' in steps):
        print('extracting the translations...')
        translations = [
            data_extractor.extract_translations(english_page['title'],
                                                english_page['wikicode'],
                                                language='German')
            for english_page in tqdm(english_pages)
        ]
        data_sizes['translations-extract'] = len(translations)
        translation_texts = []
        for translation_set in translations:
            translation_texts += [ (t['entry_name'], t['meaning'], t['translations']) for t in translation_set ]
        data_sizes['translations-texts'] = len(translation_texts)
    translation_templates = None
    if('translation-templates' in steps):
        print('extracting the translation templates...')
        translation_templates = data_extractor.list_all_templates([ t[-1] for t in translation_texts])
        data_sizes['translation-templates'] = len(translation_templates)
    return {
        'data_sizes': data_sizes,
        'pages_data': pages_data,
        'english_pages': english_pages,
        'german_pages': german_pages,
        'translations': translations,
        'translation_texts': translation_texts,
        'translation_templates': translation_templates,
    }

def save_translation_htmls(context_data: list[dict],
                           translation_htmls: list[str],
                           save_path: str = 'ignored/translations.html',
                           do_sort: bool=False):
    translation_entries = []
    for context, translations in zip(context_data, translation_htmls):
        if(translations == ''):
            continue
        entry_name = context[0]
        if(entry_name.endswith('/translations')):
            entry_name = entry_name[:-13]
        meaning = context[1]
        translation_entry = f'<b>{entry_name}</b>'
        if(meaning != ''):
            translation_entry += f' ({meaning})'
        translation_entry += f': {translations}'
        translation_entries.append(translation_entry)
    if(do_sort):
        translation_entries = sorted(translation_entries, key=str.casefold)
    translations_in_a_list = '<ol>\n<li>' + '</li>\n<li>'.join(translation_entries) + '</li>\n</ol>'
    translations_html = '<html><head><style>'
    with open('css/dict.css', 'r') as style_file:
        style = style_file.read()
    translations_html += '\n' + style + '\n'
    translations_html += '\n</style></head><body>' + translations_in_a_list + '</body></html>'
    with open(save_path, 'w') as f:
        f.write(translations_html)


def save_extracted_translations(context_data: list[dict],
                                translation_htmls: list[str],
                                save_path: str = 'ignored/translations.json',
                                do_sort: bool=False):
    translation_entries = []
    for context, translations in zip(context_data, translation_htmls):
        if(translations == ''):
            continue
        entry_name = str(context[0])
        if(entry_name.endswith('/translations')):
            entry_name = entry_name[:-13]
        meaning = str(context[1])
        translation_entry = {
            'entry': entry_name,
            'meaning': meaning,
            'translations_html': translations,
        }
        translation_entries.append(translation_entry)
    if(do_sort):
        translation_entries = sorted(translation_entries, key=lambda e: (e['entry']+e['meaning']).casefold())
    with open(save_path, 'w') as save_file:
        json.dump(translation_entries, save_file)
#

importlib.reload(data_extractor)
importlib.reload(html_formatter)
importlib.reload(wiki_urls)
importlib.reload(wiki_to_html)



chunk_paths = data_extractor.split_database(db_file_path,
                                            'ignored',
                                            filter_languages=['English', 'German'],
                                            max_size=24_000,
                                            do_overwrite=False)
compiler = wiki_to_html.WikiCompiler()


start_chunk_i = 0
end_chunk_i = 16

# 28:31 fine

for chunk_i, chunk_path in enumerate(chunk_paths[start_chunk_i:end_chunk_i]):
    chunk_real_index = chunk_i+start_chunk_i
    print(f'processing chunk {chunk_real_index} ("{chunk_path})')
    extraction_outputs = main_process(db_file_path=chunk_path,)
    translation_texts = [ t[-1] for t in extraction_outputs['translation_texts'] ]
    compiler.reset_status()
    translation_htmls = compiler.convert_to_html(translation_texts)
    html_file_path = f'ignored/translations-chunk-{chunk_real_index:02d}.html'
    json_file_path = f'ignored/translations-chunk-{chunk_real_index:02d}.json'
    print(f'saving html to "{html_file_path}"')
    save_translation_htmls(extraction_outputs['translation_texts'],
                           translation_htmls,
                           save_path=html_file_path,
                           do_sort=True)
    print(f'saving data to json file: "{json_file_path}"')
    save_extracted_translations(extraction_outputs['translation_texts'],
                                translation_htmls,
                                save_path=json_file_path,
                                do_sort=True)
    compiler.show_status()
