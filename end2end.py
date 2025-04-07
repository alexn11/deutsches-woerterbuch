import argparse
import os
import subprocess

from extract_main_loop import language_names_to_tag

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--source-lang', type=str, default='English', help='source language')
arg_parser.add_argument('--target-lang', type=str, default='German', help='target language')
arg_parser.add_argument('--db-file', type=str, default='data/dump-data.db', help='dump sqlite file')
arg_parser.add_argument('--dest-folder', type=str, default='data', help='destination folder')
arg_parser.add_argument('--initial-chunk-size', type=int, default=4000)
parsed_args = arg_parser.parse_args()
source_lang = parsed_args.source_lang
target_lang = parsed_args.target_lang
db_file_path = parsed_args.db_file
dest_folder = parsed_args.dest_folder
initial_chunk_size = parsed_args.initial_chunk_size

os.makedirs('ignored', exist_ok=True)

# extraction
print('🐁 extraction...')
try:
    subprocess.run([
        'python', 'extract_main_loop.py',
        '--db-file', db_file_path,
        '--source-lang', source_lang,
        '--target-lang', target_lang,
        '--initial-chunk-size', initial_chunk_size,
        ],
        check=True,)
except subprocess.CalledProcessError:
    print('extraction failed')
    raise

print('🐁 merging...')
subprocess.run([
    'python',
    'json-merger.py',
    '--source-lang', source_lang,
    '--target-lang', target_lang,
    '--source-folder', 'ignored',
    '--dest-folder', dest_folder,
    ],
    check=True)

print(f'🐁 conversion to html...')
subprocess.run([
    'python', 'json-to-html.py',
    '--json-file', os.path.join(dest_folder, f'translations-{language_names_to_tag(source_lang, target_lang)}.json')
    ],
    check=True)



