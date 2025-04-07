import argparse
import json

from extract_main_loop import save_translation_htmls

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--json-file', type=str, default='data/translations-eng-ger.json', help='source json file')
parsed_args = arg_parser.parse_args()

json_file_path = parsed_args.json_file
html_file_path = json_file_path[:-4] + 'html'
style_file_path = 'css/dict.css'

with open(json_file_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# keys: entry, meaning, translations_html
context_data = [
    (item['entry'], item['meaning'],)
    for item in data
]

translation_htmls = [
    item['translations_html']
    for item in data
]

# that's a silly argument format but i dont want to rewrite this function just for the arguments
save_translation_htmls(context_data,
                       translation_htmls,
                       save_path = html_file_path,
                       style_file_path = style_file_path,
                       do_sort=False) # it's already sorted

