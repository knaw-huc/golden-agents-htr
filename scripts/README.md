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
