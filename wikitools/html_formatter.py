def make_simple_tag(name: str):
    return f'<{name}>'

def make_end_tag(name: str):
    return f'</{name}>'

def make_tag(name: str, end=False, args:dict|None = None):
    if(args is None):
        return make_simple_tag(name, end=end)
    tag_args = ' '.join(f'{k}="{v}"' for k,v in args) # note: yeah ignore edgecase
    return make_simple_tag(name + ' ' + tag_args, end=end)

def make_simple_tag_block(name: str, content: str) -> str:
    return make_simple_tag(name) + content + make_end_tag(name)

def make_tag_block(name: str, content: str, args: dict) -> str:
    return make_tag(name, args=args) + content + make_end_tag(name)

def apply_format(format: str, content: str) -> str:
    return make_simple_tag_block(format, content)

def make_link(url: str, text: str|None=None, css_class: str|None = None) -> str:
    if(text is None):
        text = url
    args = {'href': url}
    if(css_class is not None):
        args['class'] = css_class
    return make_tag_block('a', text, args=args)

def apply_span_class(css_class: str, content: str) -> str:
    return make_tag_block('span', content, args={'class': css_class})

def apply_div_class(css_class: str, content: str) -> str:
    return make_tag_block('div', content, args={'class': css_class})