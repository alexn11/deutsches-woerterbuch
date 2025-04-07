import argparse
import glob
import json
import os

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--source-lang', type=str, default='English', help='source language')
arg_parser.add_argument('--target-lang', type=str, default='German', help='target language')
arg_parser.add_argument('--source-folder', type=str, default='ignored', help='source folder')
arg_parser.add_argument('--dest-folder', type=str, default='data', help='destination folder')
parsed_args = arg_parser.parse_args()

source_lang = parsed_args.source_lang
target_lang = parsed_args.target_lang
source_folder = parsed_args.source_folder
dest_folder = parsed_args.dest_folder

basename_pattern = f'translations-chunk-{source_lang[:3].lower()}-{target_lang[:3].lower()}-*.json'
file_pattern = os.path.join(source_folder, basename_pattern)

data = []
for file_path in glob.glob(file_pattern):
    print(f'appending the content of "{file_path}"')
    with open(file_path, 'r', encoding='utf-8') as json_file:
        file_data = json.load(json_file)
    data += file_data

data = sorted(data, key=lambda e: (e['entry']+e['meaning']).casefold())

dest_file_path = os.path.join(dest_folder, f'translations-{source_lang[:3].lower()}-{target_lang[:3].lower()}.json')
with(open(dest_file_path, 'w', encoding='utf-8')) as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=2)







