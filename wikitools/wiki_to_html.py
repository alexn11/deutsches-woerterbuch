import re

from mwparserfromhell.nodes import Template
from mwparserfromhell.parser import Parser as WikiParser
from mwparserfromhell.wikicode import Wikicode

from wikitools.html_formatter import apply_span_class, make_link
from wikitools.wiki_urls import make_url, make_wikipedia_url

def process_g_template(wiki: Template):
    return apply_span_class('gender-indication', str(wiki.get(1)))

def process_link_template(wiki: Template):
    entry_name = str(wiki.get(2))
    language = str(wiki.get(1))
    return make_link(url=make_url(entry_name, language=language),
                     text=entry_name,
                     css_class='default-link')

def process_gloss_template(wiki: Template):
    return apply_span_class('gloss', f'({wiki.get(1).value})')

def process_i_template(wiki: Template) -> str:
    return apply_span_class('italic', str(wiki.get(1)))

def process_ngd_template(wiki: Template) -> str: # no idea what this is but appears in italic
    return apply_span_class('italic', str(wiki.get(1)))

def process_IPAchar_template(wiki: Template):
    return apply_span_class('IPA', str(wiki.get(1)))

def process_wikipedia_link_template(wiki: Template):
    link_text = str(wiki.get(1))
    if((len(wiki.params) == 1) or wiki.has_param('lang')):
        entry_name = link_text
    else:
        try:
            entry_name = str(wiki.get(2))
        except ValueError:
            print(f'*** wiki={wiki}, params={wiki.params}')
            raise
    return make_link(url=make_wikipedia_url(entry_name),
                     text=link_text,
                     css_class='default-link')

class WikiCompiler:

    def __init__(self, skip_style_tags=True, link_target_language: str = 'German'):
        self.parser = WikiParser()
        self.skip_style_tags = skip_style_tags
        self.link_target_language = link_target_language
        self.skipped_templates = [
            'attention',
            'no equivalent translation',
            'no_equivalent_translation',
            'not used',
            'rfgender',
            'rfv-sense',
            't-check',
            't+check',
            't-needed',
        ]
        self.reset_status()

    def reset_status(self,):
        self.errors = []
        self.ignored_templates_ct = 0
        self.unexpected_templates = []
        self._has_link = []

    def show_status(self,):
        print(f'ignored templates: {self.ignored_templates_ct}')
        print(f'= errors =')
        if(len(self.errors) == 0):
            print('no error')
        for error in self.errors:
            print(f' - {error}')
        print(f'= unexpected_templates =')
        if(len(self.unexpected_templates) == 0):
            print('no unexpected templates')
        for template in self.unexpected_templates:
            print(f' - {template}')

    def parse(self, wiki_text: str) -> Wikicode:
        return self.parser.parse(wiki_text, skip_style_tags=self.skip_style_tags)

    def process_mention_template(self, wiki: Template) -> str:
        mention_content = wiki.get(2).value
        return apply_span_class('mention', self.convert_wikicode_to_html(mention_content))

    def process_qualifier_template(self, wiki: Template) -> str:
        template_arg = wiki.get(1)
        template_arg_value = template_arg.value
        qualifier_content = self.convert_wikicode_to_html(template_arg_value)
        self._has_link.pop()
        return apply_span_class('qualifier', f'({qualifier_content})')

    def process_sense_template(self, wiki: Template) -> str:
        template_arg = wiki.get(1)
        template_arg_value = template_arg.value
        qualifier_content = self.convert_wikicode_to_html(template_arg_value)
        self._has_link.pop()
        return apply_span_class('sense', f'({qualifier_content}):')

    def process_translingual_taxonomic_template(self, wiki: Template) -> str:
        self._has_link[-1] = True
        entry_name = str(wiki.get(1))
        language = 'Translingual'
        return make_link(url=make_url(entry_name, language=language),
                         text=entry_name,
                         css_class='default-link')

    def process_translation_template(self, wiki: Template) -> str:
        params = wiki.params
        language_code = params[0]
        entry_name = self.convert_wikicode_to_html(params[1].value)
        has_link = self._has_link.pop()
        alt_param = None
        lit_text = ''
        optional_args = []
        for param in params[2:]:
            if(param.startswith('alt=')):
                alt_param = str(param[4:]) # NOTE: should be recursively parsed instead...
            elif(param.startswith('lit=')):
                lit_param = str(param[4:]) # NOTE: should be recursively parsed instead...
                lit_text = f'(literally “{lit_param}”)'
            else:
                param_str = str(param)
                if(param_str == '?'): # gender information missing from the dictionary
                    continue
                if(param_str.endswith('-p')): # plural indication
                    param_str = param_str[:-2] + ' pl'
                optional_args.append(param_str) # NOTE: should be recursively parsed instead...
        if(has_link):
            translation_main_bit = entry_name
        else:
            url = make_url(str(entry_name), language_code=str(language_code))
            if(url is None):
                raise Exception('url is none')
            link = make_link(url=url, text=entry_name, css_class='translation-link')
            translation_main_bit = link
        formatted_translation = translation_main_bit
        if(len(optional_args) > 0):
            optional_args = ' or '.join(optional_args)
            formatted_translation += ' ' + apply_span_class('gender-indication', optional_args)
        if(lit_text != ''):
            formatted_translation += ' ' + lit_text
        return formatted_translation

    def process_template(self, wiki: Template) -> str:
        template_name = wiki.name
        processed_wiki = ''
        self._has_link.append(False)
        if(template_name in self.skipped_templates):
            processed_wiki = ''
            self.ignored_templates_ct += 1
        else:
            match template_name:
                case 'g':
                    processed_wiki = process_g_template(wiki)
                case 'gloss':
                    processed_wiki = process_gloss_template(wiki)
                case 'i':
                    processed_wiki = process_i_template(wiki)
                case 'IPAchar':
                    processed_wiki = process_IPAchar_template(wiki)
                case 'l':
                    self._has_link[-1] = True
                    processed_wiki = process_link_template(wiki)
                case 'm' | 'mention':
                    processed_wiki = self.process_mention_template(wiki)
                case 'ngd': # no idea what this is
                    processed_wiki = process_ngd_template(wiki)
                case 'q' | 'qual' | 'qualifier' | 'qf' | 'q-lite':
                    processed_wiki = self.process_qualifier_template(wiki)
                case 's' | 'sense':
                    processed_wiki = self.process_sense_template(wiki)
                case 't' | 't+' | 'tt' | 'tt+':
                    processed_wiki = self.process_translation_template(wiki)
                #case 't-check' | 't+check' | 't-needed' | 'no equivalent translation' | 'attention' | 'rfv-sense ' | 'not used':
                #    processed_wiki = ''
                #    self.ignored_templates_ct += 1
                case 'taxfmt':
                    processed_wiki = self.process_translingual_taxonomic_template(wiki)
                case 'w':
                    processed_wiki = process_wikipedia_link_template(wiki)
                case _:
                    self.unexpected_templates.append((template_name, wiki))
        return processed_wiki

    def convert_wikicode_to_html(self, wiki_code: Wikicode) -> str:
        processed_content = ''
        #print(f'MAIN: input="{wiki_code}" ({type(wiki_code)})')
        for node in wiki_code.nodes:
            #print(f'MAIN: node="{node}"')
            if(isinstance(node, Template)):
                #print('MAIN: > template')
                converted_node = self.process_template(node)
            else:
                #just append the node as str
                #print('MAIN: > anything else')
                converted_node = str(node)
            #print(f'MAIN: node result="{converted_node}"')
            processed_content += converted_node
        #print(f'MAIN result="{processed_content}"')
        return processed_content

    def expand_link_macros(self, wiki_text: str) -> str:
        # i cant imagine anything going wrong with using regexp
        return re.sub(r'\[\[([^\]]+)\]\]',
                      rf'{{{{l|{self.link_target_language}|\1}}}}',
                      wiki_text)

    def convert_to_html(self, wiki_texts: list[str]) -> list[str]:
        html_texts = []
        for wiki_text in wiki_texts:
            wiki_text = self.expand_link_macros(wiki_text)
            wiki_code = self.parse(wiki_text)
            html_text = self.convert_wikicode_to_html(wiki_code)
            self._has_link = []
            html_text = re.sub(r',(?: ,){1,}', ',', html_text)
            html_text = re.sub(r',(?: ,){1,}', ',', html_text)
            html_text = html_text.strip()
            if(html_text in [ ',', ';']):
                html_text = ''
            html_texts.append(html_text)
        return html_texts

