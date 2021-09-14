# Annotation Guidelines

These are annotation guidelines for annotating a variety of entities on
notarial archives from the city of Amsterdam.  Annotations are made on the
*output* of Handwritten Text Recognition (i.e. Transkribus). The aim of the
annotation project is to develop a gold-standard so we have a means to evaluate
how our well tools (e.g. Analiticcl) can find certain entities, despite
spelling variation. Spelling variation may occur due to historical variation or
HTR-errors.

The annotation task is two-fold:

1. Annotate the class of named entity
2. Annotate the closest corrected/normalized spelling
    * Use the contemporary variant, but only if it's obvious and similarly spelled; don't use a different contemporary concept that has no direct relation to the old spelling.
    * otherwise just correct any obvious HTR errors
    * use the same morphological variant, not a lemma

Do **NOT** look at the original scans. If it's not clear for a human from the
HTR output, it won't be clear for an automated system either. Just don't tag
things you can't make heads or tails of.

## Named Entity Classes

We aim to annotate the following named entities:

* **Persons**
    * given name
    * surname prefix
    * base surname
    * patroniem (optional)
* **Locations**
    * street (do not include house numbers)
    * building ('spinhuis'), names of buildings only, no street/house numbers
    * quarter ('Jordaan', 'Wijk 6')
    * room ('voorhuis', 'achterhuis','gang','keuken')
    * city (or village)
    * country (also province/region) or abstractions like 'Amerika'.
* **Objects**  - A wide range of objects (nouns), especially those that occur in notarial deeds. Tag only the noun or noun phrase, keep as small as possible.
    * **Product group**
* **Materials** - Notarial deeds often mention materials (wooden, bronze, etc). Tagging these may help finding objects.
* **Numerals** - No digits
* **Occupations**

Though our detection will probably only use/need the first levels (in bold), I suggest we annotate more precisely
so that the data is usable for more exact purposes in the future. In a similar vein, it *might* be worth also to annotate the following even though
we do not require it at this stage:

* **Dates** - Names of days, months
* **Institutions**
* **Paintings** (titles)
* **Ships** (names)
* **Book titles**

## Annotation Tool

We will be annotating using [Recogito](https://recogito.pelagios.org/). The tags should be pre-loaded, place the corrected/normalized spelling in the *comment* field (or just leave it empty if it's already identical to the form in the document). Do not use the Person/Location/Event buttons in the recogito interface.

