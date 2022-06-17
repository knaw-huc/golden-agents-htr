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
* ``exp14*`` - **Experiment 14** - Like exp13 but after a bugfix in analiticcl. Evaluated against the groundtruth data, see evaluation results below


Pass the root directory containing the Page XML data using ``make DATADIR=/path/to/data``.

Run ``make checkdeps`` to check if you have all necessary dependencies. A [LaMachine](https://proycon.github.io/LaMachine) installation is an easy way to get all dependencies installed.

Run an experiment using for instance: ``make DATADIR=/path/to/data exp13``

## Other experiments

* `NA_word2vec_experiment.ipynb` - Training a word2vec model on all HTR data with some examples of similar words. Data not included.

## Experiment 13 Results

*(conducted with analiticcl 0.4.0, input data as described by git tag `exp13` of this repo)*

Precision, Recall, F1 values are from the "subtotal" column (microaverage) that only considers the classes 'object','person','location','streetname' and 'room', as those are the only outputted in this batch. 
Full experimental output is in the ``evaluation.exp13*.log`` and ``evaluation.exp13*.tsv`` files. Configurations (i.e. exact parameter settings) are in ``nerconfig.exp13*.json``.
Values in parentheses are stricter and take not just classification, but also normalisation into account.

ID        | Description                                       | Precision      | Recall        | F1
----------|---------------------------------------------------|----------------|---------------|-----
`exp13`   | Base (arbitrary)                                  | 0.659 (0.525)  | 0.549 (0.437) | 0.599 (0.477)
`exp13b`  | Reduced maximum anagram/levenshtein distance      | 0.648 (0.503)  | 0.549 (0.426) | 0.594 (0.461)
`exp13c`  | Unigrams only                                     | 0.641 (0.503)  | 0.556 (0.436) | 0.595 (0.467)
`exp13d`  | Increased frequency weight                        | 0.618 (0.461)  | 0.522 (0.389) | 0.566 (0.422)
`exp13e`  | Include trigrams                                  | 0.661 (0.529)  | 0.555 (0.444) | 0.603 (0.483)
`exp13f`  | Increased maximum anagram/levenshtein distance    | 0.673 (0.523)  | 0.567 (0.441) | 0.615 (0.479) 
`exp13ef` | (combination)                                     | 0.671 (0.522)  | 0.562 (0.438) | 0.612 (0.476) 
`exp13g`  | case sensitive                                    | 0.651 (0.525)  | 0.537 (0.433) | 0.588 (0.475) 
`exp13h`  | Decreased frequency weight                        | 0.657 (0.519)  | 0.560 (0.443) | 0.604 (0.478)
`exp13i`  | with Language Model from ground truth subset [1]  | 0.671 (0.441)  | 0.546 (0.359) | 0.602 (0.396)
`exp13j`  | with Language Model from modern news corpora      | 0.686 (0.514)  | 0.523 (0.392) | 0.594 (0.445) 


* ``[1]`` This is the entire subset of the collection that is marked as ground truth and is a large superset of our annotated ground truth data

## Experiment 14 Results

Same as exp13, but after fixing indeterministic behaviour in analiticcl. Also after updating boedel pages, but this has no effect.

*(conducted with analiticcl 0.4.1, input data as described by git tag `exp14` of this repo)*

ID        | Description                                       | Precision      | Recall        | F1
----------|---------------------------------------------------|----------------|---------------|-----
`exp14`   | Base (arbitrary)                                  | 0.662 (0.524) | 0.550 (0.435)  | 0.601 (0.475)
`exp14a`  | without the pre-correction stage [2]              | 0.567 (0.431) | 0.485 (0.369)  | 0.523 (0.398)
`exp14b`  | Reduced maximum anagram/levenshtein distance      | 0.650 (0.494) | 0.546 (0.415)  | 0.593 (0.451) 
`exp14c`  | Unigrams only                                     | 0.637 (0.495) | 0.553 (0.430)  | 0.592 (0.461)
`exp14d`  | Increased frequency weight                        | 0.618 (0.460) | 0.519 (0.386)  | 0.564 (0.420)
`exp14e`  | Include trigrams                                  | 0.662 (0.524) | 0.550 (0.435)  | 0.601 (0.475)
`exp14f`  | Increased maximum anagram/levenshtein distance    | 0.672 (0.520) | 0.566 (0.438)  | 0.614 (0.475)
`exp14g`  | case sensitive                                    | 0.653 (0.530) | 0.539 (0.438)  | 0.590 (0.480)
`exp14h`  | Decreased frequency weight                        | 0.657 (0.511) | 0.559 (0.434)  | 0.604 (0.470)
`exp14i`  | with Language Model from ground truth subset [1]  | 0.670 (0.436) | 0.549 (0.357)  | 0.603 (0.393) 
`exp14j`  | with Language Model from modern news corpora      | 0.681 (0.505) | 0.520 (0.385)  | 0.590 (0.437)
`exp14k`  | less pruning                                      | 0.649 (0.519) | 0.546 (0.437)  | 0.593 (0.474) 
`exp14l`  | more pruning                                      | 0.673 (0.558) | 0.455 (0.378)  | 0.543 (0.451)

* ``[2]`` As the ground-truth does uses the pre-correction stage (unfortunately), this is causes mismatches and results are inaccurate

