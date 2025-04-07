

# notes


- v3: merged html file is 23Mb:
```
pandoc -s chunks-*/*.html ---metadata title="translations" -o translations-merged.html
```

- sample of 20_000 pages, gives 4790 entries with a html file size of 1.3Mb
4775 nonempty entries (~same size)

# random

50 pages/s
380000 pages
-> 2 hours

mwparserfromhell
total lines of code:
(git ls-files | xargs wc -l)
23769 total

of which within py
(git ls-files | grep '\.py' | xargs wc -l)
 11319

of which within c & h
(git ls-files | grep -e '\.c' -e '\.h' | xargs wc -l)
6362
(the tokenizer seems to be written in c)

# principal use

## en -> de
- search term in english
- get proposals: exact match first (with poten precision on meaning) then containing the word
- proposal might have several translations
- when click on proposal/translation, directed directly to the content of the corresp entry

## de -> en
can simply display a version of the wk page


## specifics
- once installed can be used offline
- updates are the only times when online is necessary





# things to be aware of

- case sensitivity
- you need the templates

# preliminary

- check the prevalence of "* German:\n*:..."
- list all the templates used in german entries (can probabaly use mwparserfromhell for that)

# priority 0

- extract "translations" boxes
- extract all the entries for german words
- do the matching

- manual extraction process

# priority 1

- matches appear when typing in search box
- poten automated extaction process

# priority 2

- add contributors list (transaltion+entry) - necessary if public app
- "update the data now?" (last dump date, new available dump date - download size)



