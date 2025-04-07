# links

explicit links:
- `[[word]]` https://en.wiktionary.org/wiki/{{word}}
- `[[word#language|word]]` https://en.wiktionary.org/wiki/{{word}}#{{language}}

# a

???
samples:
- {{a|colloquial|chiefly northern and central Germany}}
- {{a|scientific}}

# g

italic

(gender)

# gloss

within parenthesis in italic

# IPAchar

mathrm (eg inside of qualifier)

# l

args: language, word

link: https://en.wiktionary.org/wiki/{{word}}#{{language}}

# m, mention

mathrm

# ngd

(not sure if it's really non gloss)
 italic

# "not used"

like no translation, skip/ignore entry

# q, qual, qualifier, q-lite

within parenthesis in italic

# rfv-sense

"request for verification" or somthing like that (skip/ignore)

# sense, s

within parenthesis in italic followed by ":"

German: (abstract counting): eins (de), (counting objects): ein (de)

# t

args: language code, entry name + optional args + alt=display name, lit=literal translation

link:
https://en.wiktionary.org/wiki/{{entry name}}#{{language(language code)}}
(note: missing entries shouldn't have a link)

- if optional args: space then value of 1st arg (more args?)
- alt: show display name for link if alt present (how does that work?)
- lit: after other optional args, show within parenthesis after the word "literally" within double quotes:
 "(literally “{{literal translation}}”)"



(translation)

# t+

like t plus a link to the corresponding entry in the language wiktionary
in superscript & parenthesis
https://{{language code}}.wiktionary.org/wiki/{{entry name}}

between the main link & the optional args

# taxfmt

taxonomy, translingual: do not make a link (or a link with lang="Tanslingual"), show in italic

# tt, tt+

"tt" = "t"
"tt+" = "t+"

(some wiki technical thing related to lua and memory usage)

# t+check, t-check, t-needed, no equivalent translation, attention, no_equivalent_translation, rfgender

drop these

# ACHTUNG

- links within "t*" templates


# sachen überzuprüfen

- links within t templates
- max numbers of args of t templates