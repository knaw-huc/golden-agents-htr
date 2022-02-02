REPOROOT := $(shell git rev-parse --show-toplevel)
RESOURCEDIR := $(REPOROOT)/resources/
DATADIR =


# -------------------- File Indices -------------------------

htr.index:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	#An index of all HTR-files
	echo "" > htr.index
	cat "$(REPOROOT)/resources/werkvoorraad.csv" | grep -E ";HTR" | awk -F ';' '{ print $$4"" }' | xargs -L 1 -I"{}" find "$(DATADIR)/{}" -name "*.xml" >> htr.index || [ -s htr.index ]

groundtruth.index:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	#An index of all groundtruth-files
	echo "" > groundtruth.index
	cat "$(REPOROOT)/resources/werkvoorraad.csv" | grep -E ";GT" | awk -F ';' '{ print $$4"" }' | xargs -L 1 -I"{}" find "$(DATADIR)/{}" -name "*.xml" >> groundtruth.index || [ -s groundtruth.index ]

devset.lst:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	jq --raw-output 'map(.segments)' $(REPOROOT)/analiticcl-evaluation-tool/init/recogito_selection.json | grep "\"" | tr -d '",' | sed 's/^[ \t]*//' > $@ || (rm "$@" && false)

devset.index: devset.lst
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	cat devset.lst | xargs -I"{}" find "$(DATADIR)/" -name "{}.xml" > "$@"

%.index:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	find "$(DATADIR)" -name "$(basename $@).xml" > $@

# ------------------- Plain text extracted from the Page XML ---------------------------

all.txt:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	#All text extracted from the data (irregardless of whether it is HTR or ground-truth (GT))
	find "$(DATADIR)" -name "*.xml" | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > all.txt

%.txt: %.index
	cat $< | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > "$@" || (rm "$@" && false)

%.xml:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	find "$(DATADIR)" -name "$@" | xargs -I _ ln -s _ "$@"

.PHONY: texts
texts: groundtruth.txt htr.txt

# ------------------- Tokenisation ---------------------------

%.tok.txt:  %.txt
	#Tokenised version (may not be very accurate)
	ucto -L nld-historical -m -n $< $@

# ------------------- Intermediate pattern models for lexicon extraction ---------------------------

%.colibri.patternmodel: %.colibri.cls %.colibri.dat
	colibri-patternmodeller -u -l 5 -t 2 -f $*.colibri.dat -c $*.colibri.cls --outputmodel $@

%.tok.colibri.cls: %.tok.txt
	colibri-classencode $<

%.tok.colibri.dat: %.tok.txt
	colibri-classencode $<

# ------------------- Extracted lexicons ---------------------------

%.lexicon.tsv: %.colibri.patternmodel %.colibri.cls
	#Frequency lexicons from corpus
	colibri-patternmodeller -u -i $*.colibri.patternmodel -c $*.colibri.cls --print -l 1 -t 2 | tail --lines="+2" | sort -r -n -k 2 | cut -f 1,2 > $@


# ------------------- Variant matching ---------------------------

htr-normalised-against-groundtruth.analiticcl.t0.5.tsv: htr.tok.lexicon.tsv groundtruth.tok.lexicon.tsv
	#This takes the htr lexicon and finds for each entry all variants in the groundtruth lexicon (above a certain score threshold)
	cat htr.tok.lexicon.tsv | cut -f 1 | analiticcl query --score-threshold 0.5 --progress --alphabet simple.alphabet.tsv --lexicon groundtruth.tok.lexicon.tsv > htr-normalised-against-groundtruth.analiticcl.t0.5.tsv


# ------------------- Experiments (meta) ---------------------------

.PHONY: exp1
exp1: htr.tok.lexicon.tsv groundtruth.tok.lexicon.tsv

.PHONY: exp2
exp2: htr-normalised-against-groundtruth.analiticcl.t0.7.tsv

.PHONY: exp3
exp3: lexicons A16098000033.txt
	analiticcl --debug 1 search --single-thread --alphabet $(RESOURCEDIR)/simple.alphabet.tsv --lexicon $(RESOURCEDIR)/object_lexicon.tsv --lexicon $(RESOURCEDIR)/family_names_lexicon.tsv --lexicon $(RESOURCEDIR)/first_names_lexicon.tsv --lexicon $(RESOURCEDIR)/streetnames_lexicon.tsv --corpus groundtruth.tok.lexicon.tsv -N 1 -n 25 -T 1.4 --output-lexmatch < A16098000033.txt > exp3.out.txt 2> exp3.log

%.exp4.json: %.txt lexicons
	analiticcl --debug 1 search --single-thread --alphabet $(RESOURCEDIR)/simple.alphabet.tsv --lexicon $(RESOURCEDIR)/object_lexicon.tsv --lexicon $(RESOURCEDIR)/sanitized_first_names_lexicon.tsv --lexicon $(RESOURCEDIR)/sanitized_family_names_lexicon.tsv --lexicon $(RESOURCEDIR)/streetnames_lexicon.tsv -n 25 -T 1.4 --output-lexmatch --json < $< > "$@" || (rm "$@" && false)

%.exp5.json: %.txt lexicons
	analiticcl --debug 1 search --single-thread --alphabet $(REPOROOT)/resources/simple.alphabet.tsv --lexicon $(RESOURCEDIR)/object_lexicon.tsv --errors $(RESOURCEDIR)/int_lemma_hist_variants.tsv --lexicon $(RESOURCEDIR)/sanitized_first_names_lexicon.tsv --lexicon $(RESOURCEDIR)/sanitized_family_names_lexicon.tsv  --lexicon $(RESOURCEDIR)/streetnames_lexicon.tsv -n 25 -T 1.4 --output-lexmatch --json < $< > "$@" || (rm "$@" && false)

%.exp6.json: %.xml lexicons
	golden-agents-ner --stdout --config nerconfig.exp6.json "$<" > "$@" || (rm "$@" && false)

%.exp7.json: %.xml lexicons
	golden-agents-ner --stdout --config nerconfig.exp7.json "$<" > "$@" || (rm "$@" && false)

.PHONY: exp7
exp7: devset.lst lexicons
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	#recursive make procesisng the whole development set
	cat devset.lst | xargs -I"{}" make DATADIR="$(DATADIR)" "{}.exp7.json"

.PHONY: lexicons
lexicons:
	cd $(RESOURCEDIR) && make all
	cd -

# ------------------- Dependency check ---------------------------

.PHONY: checkdeps
checkdeps:
	which cut
	which find
	which awk
	which ucto
	which colibri-classencode
	which colibri-patternmodeller
	which analiticcl
	which lexmatch
	which jq
	python3 -c 'import SPARQLWrapper'
	python3 -c 'import pandas'
	which golden-agents-htr

.PHONY: help
help:
	@cat README.md
