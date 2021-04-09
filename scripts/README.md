# Various Scripts

* ``extract-text.py`` - Extracts plain text from Page XML (crudely).
* ``dehyphenize.py`` - Joins lines that end in hyphenation.


Example to extract all text from the entire collection:

```bash
find $collection_dir -name "*.xml" | xargs ./extract-text.py | ./dehyphenize.py >> all.txt
```

Example to tokenize the results using [ucto](https://languagemachines.github.io/ucto):

```bash
ucto -L nld-historical -m -n all.txt all.tok.txt
```

Example to compute frequency lists using [colibri-core](https://proycon.github.io/colibri-core) (frequency threshold 2):

```bash
colibri-classencode all.tok.txt
colibri-patternmodeller -u -l 5 -t 2 -f all.tok.colibri.dat -c all.tok.colibri.cls --outputmodel t2.colibri.patternmodel
colibri-patternmodeller -u -i t2.colibri.patternmodel -c all.tok.colibri.cls --print -l 1 | sort -r -n -k 2   > unigrams.lst
colibri-patternmodeller -u -i t2.colibri.patternmodel -c all.tok.colibri.cls --print -m 2 -l 2 | sort -r -n -k 2   > bigrams.lst
```

