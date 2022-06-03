# Golden Agents Experiments

This repository holds experimental output. The main point of entry for the experiments is the ``Makefile``, to be invoked using ``make``. It can generate the following targets for you (not exhaustive):

* ``texts``
    * ``htr.txt`` - The extracted text of all HTR data
    * ``groundtruth.txt`` - The extracted text of all Ground Truth data
* ``lexicons``
    * ``htr.tok.lexicon.tsv`` - A simple corpus-extracted lexicon with frequency count from all HTR data
    * ``groundtruth.tok.lexicon.tsv`` - A simple corpus-extracted lexicon with frequency count from all Ground Truth data
    * ``first_names_lexicon.tsv`` - Extract a simple first names lexicon (from Golden Agents Notariële Akten)
    * ``streetnames_lexicon.tsv`` - Extract a simple street names lexicon (from AdamLink)
    * ``buildings_lexicon.tsv`` - Extract a simple first names lexicon (from AdamLink)
* ``exp1`` - **Experiment 1** - Extracts simple lexicons for HTR and Groundtruth
* ``exp2`` - **Experiment 2** - Matches the HTR lexicon against the groundtruth lexicon using
    [analiticcl](https://github.com/proycon/analiticcl), finding all variants above a
    certain score threshold (``0.7``)
* ``exp9`` - **Experiment 9** - Formed the basis of the data that went to the annotators for correction (did not have context rules) 
* ``exp10`` - **Experiment 10** - Experiments with language modelling
* ``exp12*`` - **Experiment 12** - Experiments with context rules 
* ``exp13*`` - **Experiment 13** - Batch of experiments evaluated against the groundtruth data, see evaluation results below


Pass the root directory containing the Page XML data using ``make DATADIR=/path/to/data``.

Run ``make checkdeps`` to check if you have all necessary dependencies. A [LaMachine](https://proycon.github.io/LaMachine) installation is an easy way to get all dependencies installed.

Run an experiment using for instance: ``make DATADIR=/path/to/data exp13``

## Other experiments

* `NA_word2vec_experiment.ipynb` - Training a word2vec model on all HTR data with some examples of similar words. Data not included.

## Experiment 13 Results

(analiticcl 0.4.0)

Precision, Recall, F1 values are from the "subtotal" column (microaverage) that only considers the classes 'object','person','location','streetname' and 'room'

ID        | Description                                       | Precision      | Recall        | F1
----------|---------------------------------------------------|----------------|---------------|-----
`exp13`   | Base (arbitrary)                                  | 0.659 (0.525)  │ 0.549 (0.437) │ 0.599 (0.477)
`exp13b`  | Reduced maximum anagram/levenshtein distance      | 0.648 (0.503)  │ 0.549 (0.426) │ 0.594 (0.461)
`exp13c`  | Unigrams only                                     | 0.641 (0.503)  │ 0.556 (0.436) │ 0.595 (0.467)
`exp13d`  | Increased frequency weight                        | 0.618 (0.461)  │ 0.522 (0.389) │ 0.566 (0.422)
`exp13e`  | Include trigrams                                  | 0.661 (0.529)  │ 0.555 (0.444) │ 0.603 (0.483)
`exp13f`  | Increased maximum anagram/levenshtein distance    | 0.673 (0.523)  │ 0.567 (0.441) │ 0.615 (0.479) 
`exp13ef` | (combination)                                     | 0.671 (0.522)  │ 0.562 (0.438) │ 0.612 (0.476) 
`exp13g`  | case sensitive                                    | 0.651 (0.525)  │ 0.537 (0.433) │ 0.588 (0.475) 
