# Golden Agents - Entity Recognition Exploratory Plan

*Maarten van Gompel*

## Goal

Detect the following in transcribed output of the City Archive (Page XML):

1. Person names
2. Locations (in and around Amsterdam, including street-level)
3. Cultural objects

Note that especially the latter category is something that is not covered in common NER models.

## Obstacles

* We're dealing with historical language, historical spelling variations
* We're dealing with possible HTR errors

We do have two major assets:

* We have, as far as I understand, elaborate lists of
  person names, locations, and cultural objects. (not entirely sure about the
  latter). See [here](../resources/)
* The HTR quality seems quite good

## Possible Strategies

Here I investigate some possible strategies for entity recognition in the
Golden Agents project, taking into account spelling variation either caused by
diachronic variation or HTR-errors.

### Strategy #1 - Naive off-the-shelf NER

Apply known NER models (e.g. Frog or SpaCy) directly on the Page XML data.

* Pro:
  * very easy to accomplish
  * context-sensitive
* Con: Expecting very poor results:
  * this does not take spelling variation into account
  * does not use any of the specific lexicons/thesauri
  * would only be suitable for detecting generic person/location names (using existing models), not the cultural objects we are after.

### Strategy #2 - Naive matching

Ingest all kinds of lexicons and thesauri and do simple matching.

* Pro:
  * very easy to accomplish
  * directly exploits the availability of various lexicons
* Con:
  * Does not take spelling variation into account

### Strategy #3 - Post-correction via TICCL

Use TICCL (part of [PICCL](https://github.com/LanguageMachines/PICCL)) to
normalize/post-correct the text, independent of the entity detection stage.

* Pro: Existing system that hopefully delivers an acceptable normalisation (but this remains to be seen)
* Con:
  * This is a complex system (lacking clear documentation) that depends on Martin's availability to properly operate it.
  * The system is currently unmaintained (main developer retired and Martin's availability is limited).

Strategy #1, #2 or #4 could be applied on top of this and will hopefully work better.

### Strategy #4 - Train a new NER model

Train a new NER model (using e.g. Frog, SpaCy, DeepFrog or otherwise) on the basis of annotated data.

This begs the question if there is enough annotated data: I know there is some
annotated data available on the city archives with regard to person names, but
I don't know if there is any with respect to the cultural objects? Preparing
training data may present a chicken-egg problem.

This does not address the spelling variant aspect. It could be applied on top of #2.

* Pro: Context-sensitive
* Con:
    * No spelling variation
    * Require enough training data

### Strategy #5 - Formulaic language and text structure

If the documents consists of highly formulaic language and common text
structure, which is often the case with inventories. Then we could use
formulaic language as cues to detect certain entities. For example, after "voor
mij comparareerden" we often see a name, and there are itemized lists of items
followed by prices.

This, as I understand it, is part of the strategy adopted by the Republic
project, using the excellent
[fuzzy-search](https://github.com/marijnkoolen/fuzzy-search) tool by Marijn
Koolen, which takes into account spelling variation. Their strategy also
involves an extra dimensions that involves exploiting text layout (i.e.
placement on a page etc), but that involves different tooling I imagine.

* Pro: Exploits the highly structured nature of the documents, takes into account spelling variation
* Con: Relies on a small number of carefully crafted phrases, does not scale to huge numbers of phrases

### Strategy #6 - Variant matching

Ingest all kinds of gazetteers/lexicons/thesauri like in #2, but do smart matching
that takes into account spelling variants.  In essence this is comparable to
what #5 does with fuzzy matching on selected phrases, but that approach does
not scale to huge amounts of search terms and therefore matches mostly formulaic context cues.

This strategy attempts to solve that bottleneck and will allow direct matching
on a lot of content terms (names,streets, objects), based on the ingested
lexicons.  I think the scalability problem can be solved if we apply/adapt some
of the underlying smart techniques that were pioneered by Martin Reynaert in
TICCL (anagram hashing to drastically reduce the search space). So this is
essentially a specialised and slimmed down variant of #3, with a direct focus
on matching against a background vocabulary.

* Pro:
  * Directly exploits the availability of lexicons etc
  * Directly takes spelling variation into account
  * Can also be made to ingest existing variant lists such as TICCLAT.
* Con:
  * No context information, does not expand to unseen instances not in the lexicon.
    * But we can also use this to match on context cues like in #5 and use that as a basis for further entity extraction
    * That would depend on carefuly crafted phrases again
  * New implementation from scratch (this is experimental and remains to be tested, and can possibly be a bit of a time-sink)

## Suggestion

My suggestion would be that I start investigating strategy #6 and implement a
first prototype. If Martin Reynaert feels up to trying #3 then we can do that in
parallel (will provided interesting comparison material regardless of whether
we eventually adopt which strategy)

At the same time we can learn more about what Republic is doing and coordinate
with Marijn Koolen (#5).

------------------------------------------------------------------

## Advice from Rutger and Marijn

We spoke with Rutger van Koert and Marijn Koolen about the project and the
approach to extract entities.

Some recommendations we received:

* Use document structure, parse into logical blocks.
    * We can use indentation cues, as well as vertical whitespace, to identify blocks that describe a single item.
    * When using document structure, rely mainly on the baseline information in the Page XML, text lines may be slanted upward/downward.
    * The Page Region information can be mostly ignored, or should at least not be taken to be too accurate.
    * Bottom line: study the document structure well and make use of it
* Marijn's approach in Republic (which I [listed](entity-recognition-plan.md) as strategy #5) relies on fuzzy-search of formulaic phrases
  that are indicative of certain entities (e.g. names).
    * This is embedded in an iterative approach where a transformation of physical structure to logical units (paragraphs, sections) is attempted
    * Marijn has a [fuzzy-search](https://github.com/marijnkoolen/fuzzy-search) tool and a [parsing library](https://github.com/HuygensING/republic-project/tree/master/republic/parser) for PageXML.
        * It works great, especially with longer phrases.
    * Focus on high-precision first and slowly improve recall (again an iterative procedure)
        * Focus on the low-hanging fruit first (e.g. bedsheets, pillows, etc)
        * Researchers tend to get frustrated when tools produce a fair amount of noise (Harm)
    * We could use locations like "in the voorhuis" as indicative phrases (Leon)
        * This grouping by rooms is seen later in time whereas older text tent to use more material adjectives (Harm)
    * Variant matches contextualize and strengthen eachother

### Suggestion 2

There are aspects which are very specific to the data collection (or parts of
it), and there are generic aspects (such as doing variant matching).  In my
explorations of strategy #6 I'm departing from the very generic viewpoint
(efficient variant matching/identification that scales). I would recommend we
similtaneously start explorations from the very specific end of things,
processing the physical document structure into logical units, and divide our
manpower here as these are initially independent endeauvours. We can then meet
ideally in the middle and tie these systems together: apply the improved variant
matching suggested in #6 on the logical blocks of data that is extracted from
a preprocessing pipeline.

------------------------------------------------------------------

## Initial feasibility report regarding Strategy #6

*(May 4, 2021)*

These past weeks, I've been working on [Analiticcl](https://github.com/proycon/analiticcl), which implements the ideas
suggested for stategy #6, inspired on techniques researched by Martin Reynaert. As mentioned, I'm working at the very
generic end of things here. Bram has been recruited into the project to work on the more specific end.

Analiticcl allows efficient approximate string matching against one or more lexicons. Given an input string that may
contain HTR errors or historical variants, the closest matching items from the lexicon are returned. See the
[Analiticcl git repository](https://github.com/proycon/analiticcl) for a more complete overview of features and
abilities.

Multiple lexicons may be passed to analiticcl, optionally including frequency information. Lexicons can be quite large
(as in a few hundred thousand items) and the actual matching of a variant and returning of candidates occurs in a
fraction of a second. Initial loading of lexicons and building time of the search indices is a matter of a few seconds
to a minute. Lexicon entries that match can be returned along with the lexicon they were found it, allowing us to use
this as a simple form of tagging if we use different lexicons for names, locations, inventory items, etc...

I conducted some initial [experiments](https://github.com/knaw-huc/golden-agents-htr/tree/master/experiments). An initial impression of the output can be found in [htr.matchedvariants.json](https://download.anaproy.nl/htr.matchedvariants.json) (WARNING: 580MB!). This came about as follows:

* I first derived a lexicon of all words in the HTR data of our collection. Note that this is based on a very
rough extraction from the Page XML and a very rough tokenisation, with total disregard for the actual document structure.
* I did the same for the ground truth portion of the data.
* I extracted some reference lexicons for first names, surnames and street names from the Linked Data collections
  described in ``resources/``.
* I matched all types in the HTR-derived lexicon against several reference lexicons.

The first conclusion here is that the matching strategy works well and scales. The quality is very dependent on the quality of
the reference lexicons and the weights assigned to the different metrics.

There are two related major components to implement in a second stage still: actual matching on (untokenised) running
text and handling of n-grams so we can handle split/merges and handle a bit of context information. These are not trivial but are important.

Implementation of this new tool has been a significant time-sink (but a very fun and worthwhile effort I'd say),
implementation of the second stage will likely be similar.


## Current status

*(Aug 3, 2021)*

I have picked up work again on the second stage of analiticcl, the matching on untokenised running text and handling of
n-grams and consideration of context. This is a complicated matter which I describe in further detail in [this issue](https://github.com/proycon/analiticcl/issues/2).

The use-case I descibe there may seem more like classical spelling detection and correction than the specific entity
recognition problem we are dealing with in Golden Agents, but that is the approach we have chosen: we are tackling the
spelling variation and entity-detection problem in one.

We may need to slowly start thinking about how to set up the full tagging pipeline. The pipeline takes PageXML, does
parsing and selection (Bram's part), passes text snippets it has determined to be useful units to analitticl for
detection and tagging (parameterised by a whole bunch of input/background lexicons) and the scripts pick up the results
and handle storage somewhere. The main difficulty here, which has a direct effect on the accuracy of the detected entities,
is selecting the right combination of input/background lexicons, confusions lists, etc.. for analiticcl. This requires
considerable experimentation.

We will need some manually tagged subset of the data for evaluation purposes, I think Harm already did some work to that
end, and I think there are already parts of the data that already have some entity detection?

## Current status

*(Oct 18, 2021)*

Significant work has been performed on analiticcl in the past three months, culminating in the
[v0.3.0](https://github.com/proycon/analiticcl/releases/tag/v0.3.0) release. The release notes describe the changes in
more technical detail, and the [README](https://github.com/proycon/analiticcl/blob/master/README.md) provides an
up-to-date overview of the possibilities so-far. A Python binding is released and is used to invoke analiticcl for the
collection-specific parts of the pipeline developed by Bram.

The scoring mechanism has been revised and handling of n-grams and context has been implemented as described in
[issue #2](https://github.com/proycon/analiticcl/issues/2). Context consideration is implemented using a simple n-gram
language model that scores the top-n hypotheses that emerge from the variant model, for the entire input.
This effectively combines two models (variant model and language model), and that always brings the challenge of
weighing the scores of these components in such a way to get the best results. That is not a trivial matter nor an exact science,
and striking the right balance should ideally be done empirically, which leads us to the next issue:

As I suggested in the last status, a small gold-standard set is needed to evaluate the performance of analiticcl (and
surrounding pipeline). The annotation task has been fully set up now and the annotations can start annotating according
to [these annotation
guidelines](https://github.com/knaw-huc/golden-agents-htr/blob/master/docs/annotation-guidelines.md).

As also indicated earlier, the quality of the output is very dependent on the quality of the input lexicons, and a decent
general background lexicon is an important component in that equation. After all, analiticcl will eagerly attempt to
match what it sees at test time to anything in the lexicon. If the lexicon has poor coverage, than the change of false
positives increases. We have some ground to gain in doing some lexicon curation (either semi-automatically or in part
manually). I've done some initial experiments using an outdated version of the INT Historical Lexicon (a new version has
been requested) ([example output](https://github.com/knaw-huc/golden-agents-htr/blob/master/docs/annotation-guidelines.md)), some experiments with TICCLAT as input lexicon will also be conducted soon.





