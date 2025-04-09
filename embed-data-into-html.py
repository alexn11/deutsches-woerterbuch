import argparse
import json
import os

from extract_main_loop import language_names_to_tag

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--source-lang', type=str, default='English', help='source language')
arg_parser.add_argument('--target-lang', type=str, default='German', help='target language')
arg_parser.add_argument('--data-folder', type=str, default='data')
arg_parser.add_argument('--html-template', type=str, default='html/search.html')
arg_parser.add_argument('--output-dir', type=str, default='html')
arg_parser.add_argument('--style', type=str, default='css/dict.css')
parsed_args = arg_parser.parse_args()

source_lang = parsed_args.source_lang
target_lang = parsed_args.target_lang
data_folder = parsed_args.data_folder
html_template_path = parsed_args.html_template
style_file_path = parsed_args.style

tag = language_names_to_tag(source_lang, target_lang)

dest_file_path = os.path.join(parsed_args.output_dir, f'search-{tag}.html')

with open(os.path.join(data_folder, f'translations-{tag}.json'), 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

with open(html_template_path, 'r', encoding='utf-8') as html_file:
    html_content = html_file.read()

with open(style_file_path, 'r', encoding='utf-8') as css_file:
    css_content = css_file.read()

html_content = html_content.replace('<link rel="stylesheet" href="css/dict.css">', '<style>'+css_content+'</style>')
html_content = html_content.replace('const embedded_data = false;', 'const embedded_data = ' + json.dumps(data, ensure_ascii=False) + ';')


with open(dest_file_path, 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)

