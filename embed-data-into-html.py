import json

with open('data/translations-en-de.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

with open('html/search.html', 'r', encoding='utf-8') as html_file:
    html_content = html_file.read()

with open('css/dict.css', 'r', encoding='utf-8') as css_file:
    css_content = css_file.read()

html_content.reaplce('<link rel="stylesheet" href="css/dict.css">', css_content)
html_content.replace('const embedded_data = [];', 'const embedded_data = ' + json.dumps(data, ensure_ascii=False) + ';')


with open('html/search-en-de.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)

