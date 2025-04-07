import os
import random
import sqlite3
from typing import Literal

from mwparserfromhell import parse as wikicode_parse
from mwparserfromhell.parser import Parser as WikicodeParser
from mwparserfromhell.wikicode import Wikicode
from tqdm import tqdm

end_translation_tag = '{{trans-bottom}}'

#

def connect_to_db(db_file_path: str) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(db_file_path)
    db_cursor = db_connection.cursor()
    return (db_connection, db_cursor)

def create_db(db_file_path: str) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    return connect_to_db(db_file_path)

def query_pages_from_db(db_file_path: str) -> list:
    db_connection, db_cursor = connect_to_db(db_file_path)
    page_rows = db_cursor.execute(f'select title, body from pages').fetchall()
    db_connection.close()
    return page_rows

def query_all_the_data(db_file_path: str) -> list[tuple]:
    db_connection, db_cursor = connect_to_db(db_file_path)
    data = db_cursor.execute(f'select language, title, namespace_id, body from pages').fetchall()
    db_connection.close()
    return data

def create_page_table(db_cursor: sqlite3.Cursor):
    creation_command = """create table pages (
    language TEXT,
    title TEXT,
    namespace_id TEXT,
    body TEXT,
    PRIMARY KEY(language, title, namespace_id));"""
    db_cursor.execute(creation_command)

def create_table_from_data(db_file_path: str, data: list[tuple]):
    db_connection, db_cursor = create_db(db_file_path)
    create_page_table(db_cursor)
    for row in data:
        db_cursor.execute('insert into pages(language, title, namespace_id, body) values (?, ?, ?, ?)', row)
    db_connection.commit()
    db_connection.close()

#

def make_section_header_string(language: str) -> str:
    return f'=={language}=='

def make_translation_line_string(language: str) -> str:
    return f'* {language}:'

def quick_page_filter(page_body: str, filter_strings: list[str]):
    return any(filter_string in page_body for filter_string in filter_strings)

def finer_quick_filter(page_body: str, base_filter: str, required_strings: list[str]):
    if(base_filter not in page_body):
        return True
    return all(required_string in page_body for required_string in required_strings)


def parse_pages_wiki(pages: list[dict]) -> list[dict]:
    parser = WikicodeParser()
    for page in tqdm(pages):
        page['wikicode'] = parser.parse(page['body'], context=0, skip_style_tags=True)
    return pages

def filter_query_results(filter_languages: list[str],
                         pages_data: list[tuple],
                         filter_column_i: int = 0,) -> list[tuple]:
    # NOTE: i could just apply these filters directy in the sql query...
    language_quick_filters = [
        make_section_header_string(language)
        for language in filter_languages
    ]
    pages = [
        page
        for page in tqdm(pages_data)
        if(quick_page_filter(page[filter_column_i], language_quick_filters)
           and
           finer_quick_filter(page[filter_column_i],
                              language_quick_filters[0],
                              [ make_translation_line_string(filter_languages[1]),
                               '{{trans-top' ])) # wiki parse is very slow
    ]
    return pages

def prepare_pages(db_file_path: str,
                  filter_languages: list[str] = ['English', 'German'],
                  sample_size: int = 0,
                  skip_parsing=False) -> list[dict]:
    # note: 1st language in the list is the base language, 2nd is the target language
    print(f'fetching pages from database')
    page_rows = query_pages_from_db(db_file_path)
    print(f'fetched {len(page_rows):_} pages')
    pages = filter_query_results(filter_languages, page_rows, filter_column_i=1)
    pages = [
        {
            'title': page[0],
            'body': page[1],
        }
        for page in pages
    ]
    print(f'filtered down to {len(pages):_} pages')
    if(sample_size > 0):
        print(f'sampling {sample_size:_} pages')
        pages = random.sample(pages, sample_size)
    if(skip_parsing):
        return pages
    print(f'about to parse {len(pages):_} pages')
    parse_pages_wiki(pages)
    print(f'prepared {len(pages):_} pages')
    return pages


def filter_language(pages_data: list[dict], language: str = 'German') -> list[dict]:
    selectect_language__header = f'=={language}=='
    language_pages = []
    for page_data in tqdm(pages_data):
        page_wiki = page_data['wikicode']
        page_sections = page_wiki.get_sections(levels=[2], include_headings=True)
        section_found = False
        for section in page_sections:
            section_header = section.get(0).strip().replace(' ', '')
            section_found = section_header == selectect_language__header
            if(not section_found):
                continue
            break
        if(not section_found):
            continue
        filtered_page = {
            k: v
            for k, v in page_data.items() if (k != 'wikicode')
        }
        filtered_page['wikicode'] = section
        language_pages.append(filtered_page)
    return language_pages


def extract_translations(entry_name: str, page_wiki: Wikicode, language: str = 'German',) -> list[dict]:
    page_templates = page_wiki.filter_templates()
    translation_templates = [
        template for template in page_templates
        if(template.name.matches('trans-top'))
    ]
    language_filter_line = f'* {language}:'
    translations = []
    for template in translation_templates:
        errors = []
        translations_start = page_wiki.find(str(template))
        translations_end = translations_start + page_wiki[translations_start:].find(end_translation_tag)
        # split into lines, keep only the lines that start with the selected language, etc
        translation_lines = page_wiki[translations_start:translations_end].split('\n')
        translation_lines = [
            line for line in translation_lines
            if line.startswith(language_filter_line)
        ]
        if(len(translation_lines) == 0):
            continue
        if(len(translation_lines) != 1):
            errors.append(f'more than one entry (={len(translation_lines)}) in transations block')
            #raise Exception(f'{template} : ({len(translation_lines)}) {translation_lines}')
        try:
            x = str(template)
        except(ValueError):
            print(template)
            raise
        try:
            meaning = template.get(1).value
        except(ValueError): # no specification of meaning
            meaning = ''
        translation = {
            'entry_name': entry_name,
            'code': '\n'.join([str(template), '\n'.join(translation_lines), end_translation_tag]),
            'meaning': meaning,
            'translations': translation_lines[0][len(language_filter_line):].strip(),
            'errors': errors,
        }
        translations.append(translation)
    return translations

def list_all_templates(pages_wiki: list[str]) -> list[dict]:
    parser = WikicodeParser()
    templates = {}
    for page_wiki in pages_wiki:
        page_wiki = parser.parse(page_wiki, skip_style_tags=True)
        page_templates = page_wiki.filter_templates()
        for template in page_templates:
            template_name = str(template.name)
            if(template_name in templates):
                continue
            templates[template_name] = [ template, page_wiki ]
    return templates


def split_database(db_file_path: str,
                   save_folder: str,
                   max_size: int = 50_000,
                   filter_languages=None,
                   do_overwrite=False) -> list[str]:
    # TODO: split the database in manageable chunks
    # save them in folder save_folder
    print(f'fetching pages from database')
    data = query_all_the_data(db_file_path)
    nb_rows = len(data)
    print(f'fetched {nb_rows:_} pages')
    if(filter_languages is not None):
        data = filter_query_results(filter_languages, data, filter_column_i=3)
        nb_rows = len(data)
        print(f'filtered down to {nb_rows:_} pages')
    db_file_name_base = os.path.basename(db_file_path)
    if(db_file_name_base.endswith('.db')):
        db_file_name_base = db_file_name_base[:-3]
    db_chunk_file_paths = []
    for chunk_i in range(0, nb_rows, max_size):
        db_chunk_file_path = os.path.join(save_folder, f'{db_file_name_base}-{chunk_i:03d}.db')
        db_chunk_file_paths.append(db_chunk_file_path)
        if((not do_overwrite) and (os.path.exists(db_chunk_file_path))):
            print(f'file already exists, skipping')
            continue
        print(f'creating database file "{db_chunk_file_paths}"')
        create_table_from_data(db_chunk_file_path, data[chunk_i : chunk_i + max_size])
    return db_chunk_file_paths
