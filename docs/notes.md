# HOW TO RUN

(in wiki venv)

## end to end

note: source-lang should always be  `English`

- copy the extracted data from the dump in a file somewhere: eg `data/dump-data.db`
- run the end to end script:
```bash
python end2end.py --db-file data/dump-data.db --dest-folder data --target-lang German
```

for small language, the chunking isnt necessary, can skip that by passing chunk size 0:
```bash
python end2end.py --db-file data/dump-data.db --dest-folder data --initial-chunk-size 0 --target-lang Nahuatl
```

convert the result into a selbstständig html datei:
```bash
python embed-data-into-html.py  --target-lang German --data-folder data 
```
### examples

```bash
python end2end.py --db-file data/dump-data.db --dest-folder data --target-lang Akkadian --initial-chunk-size 0
python embed-data-into-html.py  --data-folder data  --target-lang Akkadian
```
(note the transcription param isnt processed properly)


```bash
python end2end.py --db-file data/dump-data.db --dest-folder data --target-lang Spanish
python embed-data-into-html.py  --data-folder data  --target-lang Spanish
```

## search box

from https://dev.to/am20dipi/how-to-build-a-simple-search-bar-in-javascript-4onf

## the step by step way

- copy the extracted data from the dump in a file somewhere: eg `data/dump-data.db`
- run the main extraction (can be long and perillous):
```bash
python extract_main_loop.py --db-file data/dump-data.db --source-lang English --target-lang German
```
- now there's plenty of chunk in the `ignored` folder (i could add an argument to choose the folder, maybe one day)
- they need to be assembled together to form a single file, run
```bash
python json-merger.py --source-lang English --target-lang German --source-folder ignored --dest-folder data
```
- this file can then be converted into html
```bash
python json-to-html.py --json-file data/translations-eng-ger.json
```
- TODO: this whole thing should just be a single script (done, see above)


# notes

- v3 works fine with EN->Nahuatl ! (813 pages, 812 translations)
- v3: merged html file is 23Mb:
```
pandoc -s chunks-*/*.html --metadata title="translations" -o translations-merged.html
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



