import json
import sqlite3


db_file_path = 'data/dump-data.db'


db_connection = sqlite3.connect(db_file_path)
db_cursor = db_connection.cursor()


if False:
    word = 'month'
    results = db_cursor.execute(f'select body from pages where title="{word}"')

    page_body = results.fetchone()[0]

    import pypandoc
    html_output = pypandoc.convert_text(page_body, 'html', format='mediawiki')
    with open(f'ignored/{word}-pypandoc.html', 'w') as output_file:
        output_file.write(html_output)

    import wikitextparser


    import mwparserfromhtml





import mwparserfromhell
from mwparserfromhell import wikicode

page_rows = db_cursor.execute(f'select title, body from pages').fetchall()
pages = [
    {
        'title': page[0],
        'body': page[1],
    }
    for page in page_rows
]
text = pages[0]['body']
page_wikicode = mwparserfromhell.parse(text)


if(False):
    templates = page_wikicode.filter_templates()

    translation_templates = [
        template for template in templates
        if(template.name.matches('trans-top'))
    ]

    end_translation_tag = '{{trans-bottom}}'

    template = templates[0]
    template.name.matches('trans-top')
    #template.maketrans(?)
    translations_start = wikicode.find(str(template))
    translations_end = translations_start + page_wikicode[translations_start:].find(end_translation_tag)
    # split into lines, keep only the lines that start with the selected language, etc

    wikicode.get_tree()

    ct = 0
    for template in templates:
        if(template.name.matches('trans-top')):
            ct += 1


end_translation_tag = '{{trans-bottom}}'

def get_translations(page: wikicode.Wikicode, language: str = 'German') -> list[dict]:
    page_templates = page.filter_templates()
    translation_templates = [
        template for template in page_templates
        if(template.name.matches('trans-top'))
    ]
    language_filter_line = f'* {language}:'
    translations = []
    for template in translation_templates:
        translations_start = page.find(str(template))
        translations_end = translations_start + page[translations_start:].find(end_translation_tag)
        # split into lines, keep only the lines that start with the selected language, etc
        translation_lines = page[translations_start:translations_end].split('\n')
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

translations = get_translations(page_wikicode)

# keep only the "English" section
# loop over pages, drop the ones without english section
# keep the english section of the ones that have it

import random
page_sample = random.sample(pages, 10)

for page_data in page_sample:
    page_wikicode = mwparserfromhell.parse(page_data['body'])
    translations = get_translations(page_wikicode)
    print(f'{page_data['title']} :')
    for translation in translations:
        print(f'{page_data['title']}, {translation['meaning']}: {translation['translations']}')
    print(translations)

if(False):
    from wikitools.translations import extract_translations
    translations = extract_translations(db_cursor, start_i=0)

    print(f'extracted {len(translations)} translations')

    #print(translations)

    with open('data/translations.json', 'w') as translations_file:
        json.dump(translations, translations_file)



# keep only the "English" section
# loop over pages, drop the ones without english section
# keep the english section of the ones that have it
page_sections = page_wikicode.get_sections(levels=[2], include_headings=True)
section0 = page_sections[0]
section0.get(0).strip() == '==English=='
# etc etc



