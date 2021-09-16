REPOROOT := $(shell git rev-parse --show-toplevel)
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
	cat $< | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > $@

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

personnamesNA.csv:
	#query the Notarial Archives using the Golden Agents endpoint
	python3 "$(REPOROOT)/scripts/sparql_personnamesNA.py"

streetnamesAdamlink.csv:
	#query the AdamLink
	python3 "$(REPOROOT)/scripts/sparql_streetnamesAdamlink.py"

buildingsAdamlink.csv:
	#query the AdamLink
	python3 "$(REPOROOT)/scripts/sparql_buildingsAdamlink.py"

first_names_lexicon.tsv: personnamesNA.csv
	#Extract first names
	cut -d "," -f 3  personnamesNA.csv | sed '/^$$/d' | grep -ivE "^van$$" | tail --lines="+2" |  sort | uniq -c | sort -rn | awk '{first=$$1; $$1=""; gsub(/^[ \t]+/, "", $$0); if (length($$0) >= 3 && first > 1) { print $$0"\t"first } }' | grep -v " " | grep -v "\." | grep -v ":" | grep -v "@" > first_names_lexicon.tsv

family_names_lexicon.tsv: personnamesNA.csv
	#Extract last names
	cut -d "," -f 4,5  personnamesNA.csv | tr "," " " | sed '/^\s*$$/d' | grep -ivE "^van$$" | tail --lines="+2" | sort | uniq -c | sort -rn | awk '{first=$$1; $$1=""; gsub(/^[ \t]+/, "", $$0); if (length($$0) >= 3 && first > 1) { print $$0"\t"first } }' | grep -v " " | grep -v "\." | grep -v ":" | grep -v "@" > family_names_lexicon.tsv

streetnames_lexicon.tsv: streetnamesAdamlink.csv
	#Extract street names
	cut -d "," -f 2  streetnamesAdamlink.csv | sed '/^$$/d' | tr -d '"' | sort | uniq  > streetnames_lexicon.tsv

buildings_lexicon.tsv: buildingsAdamlink.csv
	#Extract street names
	cut -d "," -f 2  buildingsAdamlink.csv | sed '/^$$/d' | tr -d '"' | sort | uniq  > buildings_lexicon.tsv

objects.tsv:
	#Get some objects
	cut -d "," -f 1 "$(REPOROOT)/resources/objects.csv" | tail --lines="+2" > objects.tsv

sanitized_first_names_lexicon.tsv: first_names_lexicon.tsv
	"$(REPOROOT)/sanitize_lexicon.py" first_names_lexicon.tsv > sanitized_first_names_lexicon.tsv

sanitized_family_names_lexicon.tsv: family_names_lexicon.tsv
	./sanitize_lexicon.py family_names_lexicon.tsv > sanitized_family_names_lexicon.tsv

.PHONY: lexicons
lexicons: htr.tok.lexicon.tsv groundtruth.tok.lexicon.tsv sanitized_first_names_lexicon.tsv sanitized_family_names_lexicon.tsv streetnames_lexicon.tsv buildings_lexicon.tsv objects.tsv


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
exp3: objects.tsv family_names_lexicon.tsv first_names_lexicon.tsv streetnames_lexicon.tsv A16098000033.txt
	analiticcl --debug 1 search --single-thread --alphabet $(REPOROOT)/resources/simple.alphabet.tsv --lexicon objects.tsv --lexicon family_names_lexicon.tsv --lexicon first_names_lexicon.tsv --lexicon streetnames_lexicon.tsv --corpus groundtruth.tok.lexicon.tsv -N 1 -n 25 -T 1.4 --output-lexmatch < A16098000033.txt > exp3.out.txt 2> exp3.log


# ------------------- Dependency check ---------------------------

.PHONY: checkdeps
checkdeps:
	which cut
	which find
	which awk
	which ucto
	which colibri-classencode
	which colibri-patternmodeller
	python3 -c 'import SPARQLWrapper'
	python3 -c 'import pandas'

.PHONY: help
help:
	@cat README.md
