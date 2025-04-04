
def convert_language_code_to_language_name(language_code: str) -> str:
    return {
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'it': 'Italian',
        'ja': 'Japanese',
        'zh': 'Chinese',
        # Add more language codes and names as needed
    }.get(language_code, language_code)  # Default to the code itself if not found

def make_url(entry: str, language: str|None = None, language_code: str|None = None) -> str:
    url = f'https://en.wiktionary.org/wiki/{entry}'
    if(language is not None):
        url += f'#{language}'
    elif(language_code is not None):
        url += f'#{convert_language_code_to_language_name(language_code)}'
    return url