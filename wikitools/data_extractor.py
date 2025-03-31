import sqlite3


from mwparserfromhell import parse as wikicode_parse
from mwparserfromhell.wikicode import Wikicode
from tqdm import tqdm

end_translation_tag = '{{trans-bottom}}'


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
    for page in tqdm(pages):
        page['wikicode'] = wikicode_parse(page['body'])
    return pages

def prepare_pages(db_file_path: str,
                  filter_languages: list[str] = ['English', 'German']) -> list[dict]:
    language_quick_filters = [
        make_section_header_string(language)
        for language in filter_languages
    ]
    db_connection = sqlite3.connect(db_file_path)
    db_cursor = db_connection.cursor()
    page_rows = db_cursor.execute(f'select title, body from pages').fetchall()
    pages = [
        {
            'title': page[0],
            'body': page[1],
        }
        for page in page_rows
        if(quick_page_filter(page[1], language_quick_filters)
           and
           finer_quick_filter(page[1],
                              language_quick_filters[0],
                              [ make_translation_line_string(filter_languages[1]),
                               '{{trans-top' ])) # wiki parse is very slow
    ]
    parse_pages_wiki(pages)
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


def extract_translations(page_wiki: Wikicode, language: str = 'German') -> list[dict]:
    page_templates = page_wiki.filter_templates()
    translation_templates = [
        template for template in page_templates
        if(template.name.matches('trans-top'))
    ]
    language_filter_line = f'* {language}:'
    translations = []
    for template in translation_templates:
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
            raise Exception(f'{template} : ({len(translation_lines)}) {translation_lines}')
        translation = {
            'code': '\n'.join([str(template), '\n'.join(translation_lines), end_translation_tag]),
            'meaning': template.get(1).value,
            'translations': translation_lines[0][len(language_filter_line):].strip(),
        }
        translations.append(translation)
    return translations


