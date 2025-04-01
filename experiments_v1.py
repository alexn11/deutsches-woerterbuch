import cProfile
import importlib
import json

from tqdm import tqdm

from wikitools import data_extractor
importlib.reload(data_extractor)

db_file_path = 'data/dump-data.db'

pages_data = data_extractor.prepare_pages(db_file_path, skip_parsing=True, sample_size=10_000)
parsed_pages_data = data_extractor.parse_pages_wiki(pages_data)


#cProfile.run("pages_data = data_extractor.prepare_pages(db_file_path, sample_size=5000)", sort='tottime')

pages_data = data_extractor.prepare_pages(db_file_path, sample_size=5000)

#cProfile.run("data_extractor.filter_language(pages_data, language='English')", sort='cumtime')

english_pages = data_extractor.filter_language(pages_data, language='English')
german_pages = data_extractor.filter_language(pages_data, language='German')

translations = [
    data_extractor.extract_translations(english_page['wikicode'], language='German')
    for english_page in tqdm(english_pages)
]

