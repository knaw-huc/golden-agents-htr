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

Try **NOT** to look too much at the original scans. If it's not clear for a human from the
HTR output, it won't be clear for an automated system either. Just don't tag
things you can't make heads or tails of.

The purpose of this annotation project is merely to establish a development set which we can use to tweak and
evaluate the performance of our tagging tool in a more methodological fashion.

Quantity wise, we're aiming for about 10 deeds to start with.

## Named Entity Classes

We aim to annotate the following named entities:

* **Object**  - A wide range of objects (nouns), especially those that occur in notarial deeds. Tag only the noun or noun phrase, keep as small as possible.
* **Material** - Notarial deeds often mention materials (wooden, bronze, etc). Tagging these may help finding objects.
* **Property** - This contains further adjectives aside from materials that are often used with objects
* **Person**
    * at this stage, analiticcl will detect first names and family names, please retag the whole entity as **person**,
      within a person entity, don't bother correcting first names and last names. Patronyms etc are also part of the
      **person** entity.
* *Location*
    * **streetname** (do not include house numbers)
    * **country** - including abstractions like 'Amerika'.
    * **region** - provinces/regions
    * **building** ('spinhuis'), names of buildings only, no street/house numbers
    * **location** - other locations (including cities, town, quarters)
    * **room** ('voorhuis', 'achterhuis','gang','keuken'; also including immovable objects that are part of rooms like schoorsteen, bedstee)
* **Currency** - Words like 'gulden', 'daalder', 'kwartje'
* **Animal** - Animals
* **Quantifier** - Words for units (zak, partij, vat) and numerals (no digits)
* **Picture** - Words that are highly descriptive for paintings/art objects (e.g. zeeslagje)
* **Occupation** - (visser, bakker, etc)

## False positives

There will be a high amount of false positives (mistagged words) at this stage. If it's too time-consuming to correct these individually in the annotation tool, just keep a list and add the false positives to that list so it can later be handled
automatically. Make sure to mention the original form, 'corrected' form, and the tag in the list.

## False negatives

If you notice that notable words are missed, either keep a list or preferably add them directly to [boedeltermen.csv](https://github.com/knaw-huc/golden-agents-htr/blob/master/resources/boedeltermen.csv).

## Annotation Tool

We will be annotating using [Recogito](https://recogito.pelagios.org/). The tags should be pre-loaded, place the corrected/normalized spelling in the *comment* field (or just leave it empty if it's already identical to the form in the document). Do not use the Person/Location/Event buttons in the recogito interface.

