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
page_rows = db_cursor.execute(f'select title, body from pages').fetchall()
pages = [
    {
        'title': page[0],
        'body': page[1],
    }
    for page in page_rows
]
text = pages[0]['body']
wikicode = mwparserfromhell.parse(text)

templates = wikicode.filter_templates()

translation_templates = [
    template for template in templates
    if(template.name.matches('trans-top'))
]

end_translation_tag = '{{trans-bottom}}'

template = templates[0]
template.name.matches('trans-top')
#template.maketrans(?)
translations_start = wikicode.find(str(template))
translations_end = translations_start + wikicode[translations_start:].find(end_translation_tag)
# split into lines, keep only the lines that start with the selected language, etc

wikicode.get_tree()

ct = 0
for template in templates:
    if(template.name.matches('trans-top')):
        ct += 1

if(False):
    from wikitools.translations import extract_translations
    translations = extract_translations(db_cursor, start_i=0)

    print(f'extracted {len(translations)} translations')

    #print(translations)

    with open('data/translations.json', 'w') as translations_file:
        json.dump(translations, translations_file)

