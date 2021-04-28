REPOROOT := $(shell git rev-parse --show-toplevel)
DATADIR =


# Indices:

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

# Extracted text:

all.txt:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@false
endif
	#All text extracted from the data (irregardless of whether it is HTR or ground-truth (GT))
	find "$(DATADIR)" -name "*.xml" | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > all.txt

%.txt: %.index
	cat $< | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > $@

%.tok.txt:  %.txt
	#Tokenised version (may not be very accurate)
	ucto -L nld-historical -m -n $< $@

# Pattern models and extracted (decoded) lexicons:

%.colibri.patternmodel: %.colibri.cls %.colibri.dat
	colibri-patternmodeller -u -l 5 -t 2 -f $*.colibri.dat -c $*.colibri.cls --outputmodel $@

%.tok.colibri.cls: %.tok.txt
	colibri-classencode $<

%.tok.colibri.dat: %.tok.txt
	colibri-classencode $<

%.lexicon.tsv: %.colibri.patternmodel %.colibri.cls
	colibri-patternmodeller -u -i $*.colibri.patternmodel -c $*.colibri.cls --print -l 1 -t 2 | tail --lines="+2" | sort -r -n -k 2 | cut -f 1,2 > $@


.PHONY: checkdeps
checkdeps:
	which cut
	which find
	which awk
	which ucto
	which colibri-classencode
	which colibri-patternmodeller



