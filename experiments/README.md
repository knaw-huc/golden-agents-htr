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


Pass the root directory containing the Page XML data using ``make DATADIR=/path/to/data``.

Run ``make checkdeps`` to check if you have all necessary dependencies. A [LaMachine](https://proycon.github.io/LaMachine) installation is an easy way to get all dependencies installed.

## Other experiments

* `NA_word2vec_experiment.ipynb` - Training a word2vec model on all HTR data with some examples of similar words. Data not included.