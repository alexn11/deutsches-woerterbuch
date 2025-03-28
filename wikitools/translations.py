import re
import sqlite3

from tqdm import tqdm

# TODO: use the parser!

translation_block_start_head = r'\{\{trans-top'
translation_block_options_re = r'\|[^\}]+'
translation_block_start_tail = r'\}\}\n'
translation_block_end = r'\n\{\{trans-bottom\}\}'


translation_block_re = rf'{translation_block_start_head}({translation_block_options_re})?{translation_block_start_tail}((?:.*\n)+?)(?={translation_block_end}){translation_block_end}'

translation_block_re = r'\{\{trans-top(\|[^\}]+)?\}\}\n((?:.*\n)+?)(?=\{\{trans-bottom\}\})\{\{trans-bottom\}\}'

ignore_cases = [
    'only used with article}}', # bogey
    'plastic sheet or foil}}', # pack up
    'coll.}}', # pack up
    '[[urheberrechtlich]] [[geschützt]]', # copyrighted
    '{{t+|de|verankert}} ([[in]])', # vested
    '{{t+|de|ausgestattet}} ([[mit]])', # vested
    '[[marktschreierisch]]es [[Gehabe]] {{g|n}}', # puffery
    '{{t|de|"[[Himmel]]', # for crying out loud
    '[[Herrgott]]', # for crying out loud
    '[[figürlich]]}}', # fig.
    'sich einen {{t+|de|Schlagabtausch|m}} {{t+|de|liefern}}', # repartee
    '{{t|de|machen', # run for the hills
    'dass man wegkommt}}', # run for the hills
    'zu {{t+|de|jemandem}} {{t+|de|halten}}', # siding
    'police siren}}', # ding-a-ling
    'pejorative}}', # ding-a-ling
    '{{t|de|Milch-', # higgler
    'Geflügel- und Wildhändler|m}}', # higgler
    'Geflügel- und Wildhändlerin|f}}', # higgler
    "''in fraktur:'' s", # short s
    "''in antiqua:'' {{t|de|rundes s|n}}", # short s
    'rough}}', # lower the boom
    '{{t|de|Zerknittern}} (act)', # crinkling
    '{{t+|de|Knittern}} (sound)', # crinkling
    'die [[Columbiformen]]', # columbiform
    'die Columbiformes}}', # columbiform
    'die [[Kolumbiformen]]}}', # columbiform
    'neue [[Wortschöpfungen]] [[einführen]]', # neoterize
    '{{l|de|bestimmender}} {{t+|de|Faktor|m}}', # determinator
    '{{t+|de|StuK}} {{gloss|Sturmkanone}}', # SPG
    '{{t|de|[[Ja]]', # obvs
    '{{t+|de|a-Schwa|alt=a-Schwa', # a-schwa
    "''a''-Schwa|n}}", # a-schwa
    '{{t|de|Milanković-Zyklen}} (pl.)', # Milankovitch cycle
    '{{t|de|ein Mann muss tun', # one's got to do what one's got to do
    '{{t|de|tun', # one's got to do what one's got to do
    'was man nicht lassen kann}}', # one's got to do what one's got to do
    '{{t|de|Twentisch|n}} (adjective: {{t|de|twentisch}})', # Twents
    '{{t|de|Fersentalerisch|n}} (adjective {{t|de|fersentalerisch}})', # Mòcheno
    'rare}}', # renovated butter
    '{{t|de|bitte', # faites vos jeux
    'das Spiel zu machen}}', # faites vos jeux
    '{{t|de|drauf wetten}} (können)', # take to the bank
    '{{t|de|Gift drauf nehmen}} (können)', # take to the bank
    '{{t|de|wer dumm fragt', # ask a silly question, get a silly answer
    'bekommt eine dumme Antwort}}', # ask a silly question, get a silly answer
    '{{t|de|wissen', # know the drill
    'wie der Hase läuft}}', # know the drill
    '(ein wütender) {{t+|de|Einzelgänger}} (werden)', # go rogue
    '{{t+|de|auf eigene Faust}} (handeln', # go rogue
    'entscheiden etc.)', # go rogue
    '{{t+|de|eigenmächtig}} (handeln', # go rogue
    '{{t+|de|abtrünnig}} (werden)', # go rogue
    '(ein rebellischer) {{t+|de|Einzelgänger}} (werden)', # go rogue
    'i.e. with rehearsals}} {{t+|de|Leseprobe|f|lit=read rehearsal}}', # table read
    '{{t+|de|sich}} {{t+|de|verlegen}}', # sleep funny

]

no_translations = [
    #    'encyclopaedia',
    #    'gratis',
    #    'livre',
    #    'book', # book/translations
    #    'GDP',
]

multiple_languages = [
    'straddle' # it's a bogus entry with no actual translation
]


class TranslationProcessor:
    def __init__(self,
                 target_language: str = 'German',
                 do_raise_error_on_multiple_languages: bool = True):
        self.target_language = target_language
        self.language_line_start = f'* {target_language.capitalize()}:'
        self.multiple_languages = False
        self.multiple_languages_raises = do_raise_error_on_multiple_languages
        self.current_entry = ''
        self.current_entry_block = ''
        self._qualifier_ct = 0
        self._q_ct = 0
        self._ignored_ct = 0
        self._no_translation_ct = 0
    
    def filter_block(self, translation_block_content: str) -> list[str]:
        # keep only the lines with the selected language, for example
        # "* German: ..."
        if(self.current_entry in multiple_languages):
            return []
        filtered_block_lines = [
            line[len(self.language_line_start):].strip()
            for line in translation_block_content.split('\n')
            if line.startswith(self.language_line_start)
        ]
        if(any((len(l) == 0) for l in filtered_block_lines)):
            self.multiple_languages = True
            if(self.multiple_languages_raises):
                raise Exception(f'multiple language for entry: "{self.current_entry}" - block: {self.current_entry_block}')
        if(not(self.multiple_languages) and (len(filtered_block_lines) > 1)):
            raise Exception('unexpected multiple matching lines')
        return filtered_block_lines

    def split_block_line(self, block_line: str) -> list[str]:
        return [ translation.strip() for translation in re.split(', |; |,', block_line) ]
    
    def process_translation_tags(self, translation_item: str) -> str:
        # will raise if unexpected format
        format_regex = r'\{\{([^\}]+)\}\}'
        if(translation_item == ''):
            return ''
        if('{{qualifier|' in translation_item):
            self._qualifier_ct += 1
            return ''
        if('{{q|' in translation_item):
            self._q_ct += 1
            return ''
        if(translation_item.endswith(' (usually one in [[w:Scandinavia|Scandinavia]])')):
            translation_item = translation_item[:-len(' (usually one in [[w:Scandinavia|Scandinavia]])')]
        if(translation_item in ignore_cases):
            self._ignored_ct += 1
            return ''
        item_content = re.fullmatch(format_regex, translation_item)
        if(item_content is None):
            print(f'Not matching: "{translation_item}" - ..([^.]+)..')
        try:
            return re.fullmatch(format_regex, translation_item).group(1).split('|')[-1]
        except AttributeError:
            print(f'raised by: "{translation_item}"\n entry: "{self.current_entry}" - block= "{self.current_entry_block}"')
            print(f"'{translation_item}', # {self.current_entry}")
            raise

    def get_translations_from_block(self, block_body: str) -> list[str]:
        self.current_entry_block = block_body
        block_lines = self.filter_block(block_body)
        return block_lines
        #translations = []
        #for block_line in block_lines:
        #    translations += [
        #        self.process_translation_tags(translation_item)
        #        for translation_item in self.split_block_line(block_line)
        #    ]
        #return [ translation for translation in translations if(translation != '') ]

    def get_translations(self, page_body: str, title: str = '') -> list[dict]:
        self.current_entry = title
        translation_blocks = re.findall(translation_block_re, page_body)
        if(len(translation_blocks) == 0):
            self._no_translation_ct += 1
            if(title in no_translations):
                return []
            raise Exception(f'LEN0 -- "{title}": {page_body[:120]} ("{translation_block_re.replace("\n", "\\n")}")\n\'{title}\',')
        translations = [
            {
                'specific_meaning': block[0][1:],
                'translations': self.get_translations_from_block(block[1])
            }
            for block in translation_blocks
        ]
        return translations

class TranslationExtractor:

    def __init__(self, pages: list[dict], target_language: str = 'German'):
        self.pages = pages
        self.target_language = target_language
        self.processor = TranslationProcessor(target_language=target_language)
        self.translation_qualifiers_ct = 0

    def format_translation_heading(self, page_title: str, specific_meaning: str) -> str:
        specific_meaning = specific_meaning.strip()
        heading = page_title
        if(specific_meaning != ''):
            heading = f'{page_title} ({specific_meaning})'
        return heading

    def extract_from_page(self, page_title: str, page_body: str) -> list[dict]:
        extracted_translations = self.processor.get_translations(page_body=page_body, title=page_title)
        translations = [
            {
                'meaning': self.format_translation_heading(page_title, translation['specific_meaning']),
                'translations': translation['translations']
            }
            for translation in extracted_translations
        ]
        return translations
    
    def extract(self) -> list[dict]:
        translations = []
        for page in tqdm(self.pages):
            translations += self.extract_from_page(page['title'], page['body'])
        #self.translation_qualifiers_ct = self.processor.qualified_items_ct
        #self._q_ct = self.processor._q_ct
        #self._ignored_ct = self.processor._ignored_ct
        return translations







def extract_translations(db_cursor: sqlite3.Cursor, start_i = 0):
    # read the db
    page_rows = db_cursor.execute(f'select title, body from pages').fetchall()
    pages = [
        {
            'title': page[0],
            'body': page[1],
        }
        for page in page_rows[start_i:]
    ]
    # create extractor object
    extractor = TranslationExtractor(pages)
    # extract
    translations = extractor.extract()
    print(f'nb qualified items (missed): {extractor.processor._qualifier_ct}')
    print(f'small q: {extractor.processor._q_ct}')
    print(f'ignored: {extractor.processor._ignored_ct}')
    # return result
    return translations

