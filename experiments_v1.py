import json

from wikitools import data_extractor

db_file_path = 'data/dump-data.db'

pages_data = data_extractor.prepare_pages(db_file_path)
english_pages = data_extractor.filter_language(pages_data, language='English')
german_pages = data_extractor.filter_language(pages_data, language='German')




