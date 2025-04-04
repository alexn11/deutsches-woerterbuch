import cProfile
import importlib
import json

from tqdm import tqdm

from wikitools import data_extractor
importlib.reload(data_extractor)

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
            data_extractor.extract_translations(english_page['wikicode'], language='German')
            for english_page in tqdm(english_pages)
        ]
        data_sizes['translations-extract'] = len(translations)
        translation_texts = []
        for translation_set in translations:
            translation_texts += [ t['translations'] for t in translation_set ]
        data_sizes['translations-texts'] = len(translation_texts)
    translation_templates = None
    if('translation-templates' in steps):
        print('extracting the translation templates...')
        translation_templates = data_extractor.list_all_templates(translation_texts)
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

#

pages_data = data_extractor.prepare_pages(db_file_path, skip_parsing=True, sample_size=10_000)
parsed_pages_data = data_extractor.parse_pages_wiki(pages_data)


#cProfile.run("pages_data = data_extractor.prepare_pages(db_file_path, sample_size=5000)", sort='tottime')

pages_data = data_extractor.prepare_pages(db_file_path, sample_size=5000)

#cProfile.run("data_extractor.filter_language(pages_data, language='English')", sort='cumtime')

english_pages = data_extractor.filter_language(pages_data, language='English')
# len = 1661
german_pages = data_extractor.filter_language(pages_data, language='German')

translations = [
    data_extractor.extract_translations(english_page['wikicode'], language='German')
    for english_page in tqdm(english_pages)
]
# len = 1661

translation_texts = []
for translation_set in translations:
    translation_texts += [ t['translations'] for t in translation_set ]
# len = 2442

templates = data_extractor.list_all_templates(translation_texts)
# len = 13

extraction_outputs = main_process(db_file_path=db_file_path, sample_size=50_000,)
translation_templates = extraction_outputs['translation_templates']
template_names = sorted(translation_templates)



# exp 1.2

extraction_outputs = main_process(db_file_path=db_file_path, sample_size=124,)

from pprint import pprint
from mwparserfromhell.parser import Parser as WikiParser
from wikitools import wiki_to_html

translation_texts = extraction_outputs['translation_texts']
parser = WikiParser()

importlib.reload(wiki_to_html)
from wikitools import html_formatter
importlib.reload(html_formatter)
from wikitools import wiki_urls
importlib.reload(wiki_urls)
compiler = wiki_to_html.WikiCompiler()

for t in translation_texts:
    compiler.reset_status()
    print(f'*** "{t}" ***')
    h = compiler.convert_wikicode_to_html(parser.parse(t))
    print(f' -> "{h}"')
    print(f'ignored: {compiler.ignored_templates_ct}')
    print(f'unexpected templates: {compiler.unexpected_templates}')
    print(f'errors: {compiler.errors}')

htmls = compiler.convert_to_html(translation_texts)
compiler.show_status()

list_of_translations = '<ol>\n<li>' + '</li>\n<li>'.join(htmls) + '</li>\n</ol>'

with open('ignored/translations.html', 'w') as f:
    f.write(list_of_translations)


# exp 1.2.1


extraction_outputs = main_process(db_file_path=db_file_path, sample_size=2000,)

from pprint import pprint
from mwparserfromhell.parser import Parser as WikiParser
from wikitools import wiki_to_html

translation_texts = extraction_outputs['translation_texts']
parser = WikiParser()

importlib.reload(wiki_to_html)
from wikitools import html_formatter
importlib.reload(html_formatter)
from wikitools import wiki_urls
importlib.reload(wiki_urls)
compiler = wiki_to_html.WikiCompiler()

htmls = compiler.convert_to_html(translation_texts)
compiler.show_status()

list_of_translations = '<ol>\n<li>' + '</li>\n<li>'.join(htmls) + '</li>\n</ol>'

translations_html = '<html><head><style>'
translations_html += """
.gender-indication { font-style: italic; }
.gloss { font-style: italic;}
.qualifier { font-style: italic; }
.IPA { font-style: normal; } 
"""
translations_html += '\n</style></head><body>' + list_of_translations + '</body></html>'

with open('ignored/translations.html', 'w') as f:
    f.write(translations_html)



importlib.reload(wiki_to_html)
from wikitools import html_formatter
importlib.reload(html_formatter)
from wikitools import wiki_urls
importlib.reload(wiki_urls)
compiler = wiki_to_html.WikiCompiler()

htmls = compiler.convert_to_html([translation_texts[83]])












