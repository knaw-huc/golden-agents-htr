# Various Scripts

* ``extract-text.py`` - Extracts plain text from Page XML. To extract from entire collection
* ``dehyphenize.py`` - De-hyphenizations, joines lines that ended.

Example to extract all text from the entire collection:

```bash
find $collection_dir -name "*.xml" | xargs ./extract-text.py | ./dehyphenize.py >> all.txt
```




