# Lexicon Curation Guidelines

In order to detect objects that occur in the deeds, we need a decent lexicon of objects.

Currently we have [this
one](https://github.com/knaw-huc/golden-agents-htr/blob/master/resources/objects.csv),
but some data curation is needed to provide a higher quality lexicon.
Considering the limited amount of objects (slightly over 2000 entries), a
manual curation effort seems feasible. Ideally by experts who are familiar with
the contents of the deeds and the historical language.

## Guidelines

* We use a tab seperated format, one object per row, columns separated by spaces.
    * You can use CSV import/export in a spreadsheet program to edit
* Put the object in the first column, in some form of normalised spelling, preferably closest to contemporary
* Put spelling variants in subsequent columns (optional), no need to be exhaustive here because the system is designed to find spelling variants, focus on forms that deviate further from the normal form (larger edit distance) and don't bother with minor spelling variants.
* Entries without further spelling variants are fine too (first column only)
* Different forms of the object (singular, plural) should be different entries (different rows). Diminutives (-je) are considered a spelling variant rather than separate entries, unless the diminutive version of an object is a significantly different thing.
* Mind proper casing, use lowercase except for titles/names etc
* You may include multi-word entries (without determiners unless they're intrinsic part of a title/name)
* You may include compound nouns


Example:

```tsv
beddekleed	beddecleet
bed	bedde	bedje
bedden	bedjes
borduurwerk	borduerwerck
borduurwerken	borduerwercken
```










