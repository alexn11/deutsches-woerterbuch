import iso639

def get_language_code(language_name: str) -> str:
    lang_data = iso639.find(language=language_name)
    if(lang_data is None):
        language_code = language_name
    else:
        language_code = lang_data['iso639_1']
    return language_code

def convert_language_code_to_language_name(language_code: str) -> str:
    lang_data = iso639.find(iso639_1=language_code)
    if(lang_data is None):
        language_name = language_code
    else:
        language_name = lang_data['name']
    return language_name

def make_url(entry: str, language: str|None = None, language_code: str|None = None) -> str:
    url = f'https://en.wiktionary.org/wiki/{entry}'
    if(language is not None):
        url += f'#{language}'
    elif(language_code is not None):
        url += f'#{convert_language_code_to_language_name(language_code)}'
    return url

def make_wikipedia_url(entry: str) -> str:
    # TODO: proper entry formatting
    entry = entry.replace(' ', '_')
    url = f'https://en.wikipedia.org/wiki/{entry}'
    return url
