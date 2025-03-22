# read the database


- file is "enwiktionary-YYYYMMDD-pages-articles.xml.bz2
- `cd` to the folder where the file is
- run (replace YYYYMMDD with appropriate)
```bash
podman run -it --rm -v ${PWD}:/data ghcr.io/tatuylonen/wiktextract --all-languages --all --db-path data/extracted.db data/enwiktionary-YYYYMMDD-pages-articles.xml.bz2
```
- this produces a file `extracted.db`
- this is an sqlite database file
- at that point might as well run the "db extractor" script from wiktionary project: (in that folder)
```bash
python db_extractor.py --languages English,German --source-db data/2024-05/extracted.db --dest-db data/engde.db
mv data/engde.db ../deutsches-woerterbuch/data/dump-data.db
```
- now can "just" process the xml of each page in the database




