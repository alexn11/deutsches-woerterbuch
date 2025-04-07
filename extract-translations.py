# extraction script
import argparse
import gc
import importlib
import json
from pprint import pprint
import time

from tqdm import tqdm

from mwparserfromhell.parser import Parser as WikiParser

from wikitools import data_extractor
from wikitools import wiki_to_html

from wikitools import html_formatter
from wikitools import wiki_urls



#

def main_process(db_file_path: str = 'data/dump-data.db',
                 languages: tuple[str] = ('English', 'German',),
                 sample_size: int = 0,
                 pages_data: list = None,
                 steps: list = None,
                 max_pages_per_chunk: int = 0,
                 initial_offset: int = 0,
                 chunk_i: int = 0):
    source_lang, target_lang = languages
    data_sizes = {
        'init': len(pages_data) if(pages_data) else 0,
    }
    if(steps is None):
        steps = [ 'load', 'parse', 'filter-language', 'translations', 'translation-templates' ]
    print(f'running steps: {steps}')
    if('load' in steps):
        print('loading...')
        pages_data = data_extractor.prepare_pages(db_file_path,
                                                  filter_languages=languages,
                                                  skip_parsing=True,
                                                  sample_size=sample_size,
                                                  max_pages_per_chunk=max_pages_per_chunk,
                                                  initial_offset=initial_offset,
                                                  chunk_i=chunk_i)
        data_sizes['load'] = len(pages_data)
    if('parse' in steps):
        print('parsing...')
        pages_data = data_extractor.parse_pages_wiki(pages_data)
        data_sizes['parse'] = len(pages_data)
    source_lang_pages = None
    target_lang_pages = None
    if('filter-language' in steps):
        print('filtering for languages...')
        source_lang_pages = data_extractor.filter_language(pages_data, language=source_lang)
        target_lang_pages = data_extractor.filter_language(pages_data, language=target_lang)
    translations = None
    translation_texts = None
    if('translations' in steps):
        print('extracting the translations...')
        translations = [
            data_extractor.extract_translations(english_page['title'],
                                                english_page['wikicode'],
                                                language=target_lang)
            for english_page in tqdm(source_lang_pages)
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
        'source_lang_pages': source_lang_pages,
        'target_lang_pages': target_lang_pages,
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


def run_full_extraction(source_lang: str, target_lang: str,
                        chunk_size: int = 0, initial_offset: int = 0, start_chunk_i: int = 0,
                        end_chunk_i: int = -1):
    tag = f'{source_lang[:3].lower()}-{target_lang[:3].lower()}-{chunk_size}'
    chunk_i = start_chunk_i
    languages = (source_lang, target_lang,)
    compiler = wiki_to_html.WikiCompiler(link_target_language=target_lang)
    while True:
        extraction_outputs_chunk = main_process(db_file_path=db_file_path,
                                                languages=languages,
                                                max_pages_per_chunk=chunk_size,
                                                initial_offset=initial_offset,
                                                chunk_i=chunk_i,)
        nb_extracted_translation_texts = len(extraction_outputs_chunk['translation_texts'])
        if((len(extraction_outputs_chunk['pages_data']) == 0) or (nb_extracted_translation_texts == 0)):
            break
        chunk_real_index = chunk_i # +start_chunk_i
        print(f'processing chunk {chunk_real_index}')
        translation_texts = [ t[-1] for t in extraction_outputs_chunk['translation_texts'] ]
        compiler.reset_status()
        translation_htmls = compiler.convert_to_html(translation_texts)
        base_path = f'ignored/translations-{"chunk-" if(chunk_size>0) else ""}{tag}'
        html_file_path = f'{base_path}-{chunk_real_index:02d}.html'
        json_file_path = f'{base_path}-{chunk_real_index:02d}.json'
        print(f'saving html to "{html_file_path}"')
        save_translation_htmls(extraction_outputs_chunk['translation_texts'],
                            translation_htmls,
                            save_path=html_file_path,
                            do_sort=True)
        print(f'saving data to json file: "{json_file_path}"')
        save_extracted_translations(extraction_outputs_chunk['translation_texts'],
                                    translation_htmls,
                                    save_path=json_file_path,
                                    do_sort=True)
        compiler.show_status()
        if(chunk_size == 0):
            break
        time.sleep(1.25)
        print(f'collect: {gc.collect()}')
        chunk_i += 1
        if(end_chunk_i == chunk_i):
            break
    return nb_extracted_translation_texts

#

if(__name__ == '__main__'):

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--db-file', type=str, default='data/dump-data.db', help='data base file (sqlite3 file) containing the table "pages"')
    arg_parser.add_argument('--source-lang', type=str, default='English')
    arg_parser.add_argument('--target-lang', type=str, default='German')
    arg_parser.add_argument('--initial-chunk-size', type=int, default=4000)
    arg_parser.add_argument('--initial-offset', type=int, default=0)
    arg_parser.add_argument('--first-chunk-index', type=int, default=0)
    parsed_args = arg_parser.parse_args()

    db_file_path = parsed_args.db_file
    source_lang = parsed_args.source_lang
    target_lang = parsed_args.target_lang
    initial_chunk_size = parsed_args.initial_chunk_size
    initial_offset = parsed_args.initial_offset
    first_chunk_index = parsed_args.first_chunk_index

    chunk_size = initial_chunk_size

    while True:
        start_chunk_i = first_chunk_index
        while(True):
            end_chunk_i = start_chunk_i + 1
            extracted_data_indicator = run_full_extraction(source_lang, target_lang,
                                                        chunk_size=chunk_size,
                                                        initial_offset=initial_offset,
                                                        start_chunk_i=start_chunk_i,
                                                        end_chunk_i=end_chunk_i)
            if(extracted_data_indicator == 0):
                break
            if(extracted_data_indicator < 800):
                break
            if(extracted_data_indicator > 3000):
                break
            start_chunk_i += 1
        if(extracted_data_indicator == 0):
            break
        initial_offset += end_chunk_i * chunk_size
        if(extracted_data_indicator < 800):
            chunk_size *= 2
        elif(extracted_data_indicator > 3000):
            chunk_size = chunk_size // 2
        start_chunk_i = 0
