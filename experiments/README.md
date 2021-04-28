# Golden Agents Experiments

This repository holds experimental output. The main point of entry for the experiments is the ``Makefile``, which can generate the following targets (not exhaustive):

* ``htr.txt`` - The extracted text of all HTR data
* ``groundtruth.txt`` - The extracted text of all Ground Truth data
* ``htr.tok.lexicon.tsv`` - A simple corpus-extracted lexicon with frequency count from all HTR data
* ``groundtruth.tok.lexicon.tsv`` - A simple corpus-extracted lexicon with frequency count from all Ground Truth data

Pass the root directory containing the Page XML data using ``make DATADIR=/path/to/data``.

Run ``make checkdeps`` to check if you have all necessary dependencies. A [LaMachine](https://proycon.github.io/LaMachine) installation is an easy way to get all dependencies installed.
