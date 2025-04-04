import re

from mwparserfromhell.nodes import Template
from mwparserfromhell.parser import Parser as WikiParser
from mwparserfromhell.wikicode import Wikicode

from wikitools.html_formatter import apply_span_class, make_link
from wikitools.wiki_urls import make_url, convert_language_code_to_language_name

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

def process_IPAchar_template(wiki: Template):
    return apply_span_class('IPA', wiki.get(1).value)


class WikiCompiler:

    def __init__(self, skip_style_tags=True, link_target_language: str = 'German'):
        self.parser = WikiParser()
        self.skip_style_tags = skip_style_tags
        self.link_target_language = link_target_language
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

    def process_qualifier_template(self, wiki: Template) -> str:
        template_arg = wiki.get(1)
        template_arg_value = template_arg.value
        if(wiki.startswith('{{q|may be specified as') or wiki.startswith('may be specified as')):
            print(f'template arg="{template_arg}" ({type(template_arg)})')
            print(f'value: "{template_arg_value}" ({type(template_arg_value)})')
            print(f'values nodes: {len(template_arg_value.nodes)}')
            print(template_arg_value.nodes)
            #print(f's="{str(template_arg)}"')
            #print(f's(value)="{str(template_arg_value)}"')
            #raise Exception('m stopp')
        qualifier_content = self.convert_wikicode_to_html(template_arg_value)
        if(wiki.startswith('{{q|may be specified as') or wiki.startswith('may be specified as')):
            print('== result ==')
            print(qualifier_content)
            #raise Exception('mm stopp')
        self._has_link.pop()
        return apply_span_class('qualifier', f'({qualifier_content})')

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
                optional_args.append(str(param)) # NOTE: should be recursively parsed instead...
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
        match template_name:
            case 'g':
                processed_wiki = process_g_template(wiki)
            case 'gloss':
                processed_wiki = process_gloss_template(wiki)
            case 'IPAchar':
                processed_wiki = process_IPAchar_template(wiki)
            case 'l':
                self._has_link[-1] = True
                processed_wiki = process_link_template(wiki)
            case 'q' | 'qual' | 'qualifier':
                processed_wiki = self.process_qualifier_template(wiki)
            case 't' | 't+' | 'tt' | 'tt+':
                processed_wiki = self.process_translation_template(wiki)
            case 't-check' | 't+check' | 't-needed' | 'no equivalent translation' | 'attention':
                processed_wiki = ''
                self.ignored_templates_ct += 1
            case '_':
                self.unexpected_templates.append((template_name, wiki))
        return processed_wiki

    def convert_wikicode_to_html(self, wiki_code: Wikicode) -> str:
        processed_content = ''
        print(f'MAIN: input="{wiki_code}" ({type(wiki_code)})')
        for node in wiki_code.nodes:
            if(isinstance(node, Template)):
                print('MAIN: > template')
                processed_content += self.process_template(node)
            else:
                #just append the node as str
                print('MAIN: > anything else')
                processed_content += str(node)
        print(f'MAIN result="{processed_content}"')
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
            html_texts.append(html_text)
        return html_texts

