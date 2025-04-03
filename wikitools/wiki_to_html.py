from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Template

from html_formatter import apply_span_class, make_link
from wiki_urls import make_url, convert_language_code_to_language_name

def process_g_template(wiki: Template):
    return apply_span_class('gender-indication', wiki.get(1))

def process_link_template(wiki: Template):
    return make_link(url=make_url(wiki.get(2), language=wiki.get(1)), text=wiki.get(1), css_class='default-link')

def process_gloss_template(wiki: Template):
    return apply_span_class('gloss', f'({{wiki.get(1)}})')

def process_IPAchar_template(wiki: Template):
    return apply_span_class('IPA', wiki.get(1))

def process_qualifier_template(wiki: Template):
     return apply_span_class('qualifier', f'({{wiki.get(1)}})')

def process_translation_template(wiki: Template):
    params = wiki.params
    language_code = params[0]
    entry_name = process_wiki(params[1])
    alt_param = None
    lit_text = ''
    optional_args = []
    for param in params[2:]:
        if(param.startswith('alt=')):
            alt_param = param[4:]
        elif(param.startswith('lit=')):
            lit_param = param[4:]
            lit_text = f'(literally “{{{{{lit_param}}}}}”)'
        else:
            optional_args.append(param)
    url = make_url(entry_name, language_code=language_code)
    link = make_link(url=url, text=entry_name, css_class='translation-link')
    formatted_translation = link
    if(len(optional_args) > 0):
        optional_args = ' '.join(optional_args)
        formatted_translation += ' ' + optional_args
    if(lit_text != ''):
        formatted_translation += ' ' + lit_text
    return formatted_translation

def process_template(wiki: Template, process_data: dict) -> str:
    template_name = wiki.name
    processed_wiki = ''
    match template_name:
        case 'g':
            processed_wiki = process_g_template(wiki)
        case 'gloss':
            processed_wiki = process_gloss_template(wiki)
        case 'IPAchar':
            processed_wiki = process_IPAchar_template(wiki)
        case 'l':
            processed_wiki = process_link_template(wiki)
        case 'q' | 'qual' | 'qualifier':
            processed_wiki = process_qualifier_template(wiki)
        case 't' | 't+' | 'tt' | 'tt+':
            processed_wiki = process_translation_template(wiki)
        case 't-check' | 't+check' | 't-needed' | 'no equivalent translation' | 'attention':
            processed_wiki = ''
            process_data['ignored_templates_ct'] += 1
        case '_':
            process_data['unexpected_templates'].append([template_name, wiki])
    return processed_wiki

def process_wiki(wiki: Wikicode, process_data: dict):
    processed_content = ''
    process_data['errors'] = []
    process_data['ignored_templates_ct'] = 0
    process_data['unexpected_templates'] = []
    for node in wiki.nodes:
        if(isinstance(node, Template)):
            processed_content += process_template(node, process_data)
        else:
            #just append the node as str
            processed_content += node
    return processed_content