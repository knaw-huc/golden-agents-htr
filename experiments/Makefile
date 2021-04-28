REPOROOT := $(shell git rev-parse --show-toplevel)
DATADIR =

all.txt: datadir
	#All text extracted from the data (irregardless of whether it is HTR or ground-truth (GT))
	find "$(DATADIR)" -name "*.xml" | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > all.txt

all.tok.txt:  all.txt
	#Tokenised version
	ucto -L nld-historical -m -n all.txt all.tok.txt

htr.txt: htr.index
	cat htr.index | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > htr.txt

htr.tok.txt:  htr.txt
	#Tokenised version of HTR (may not be very accurate)
	ucto -L nld-historical -m -n htr.txt htr.tok.txt

groundtruth.txt: groundtruth.index
	#Tokenised version of groond truth (may not be very accurate)
	cat groundtruth.index | xargs "$(REPOROOT)/scripts/extract-text.py" | "$(REPOROOT)/scripts/dehyphenize.py" > groundtruth.txt

groundtruth.tok.txt:  groundtruth.txt
	#Tokenised version
	ucto -L nld-historical -m -n groundtruth.txt groundtruth.tok.txt

htr.index: datadir
	echo "" > htr.index
	cat "$(REPOROOT)/resources/werkvoorraad.csv" | grep -E ";HTR" | awk -F ';' '{ print $$4"" }' | xargs -L 1 -I"{}" find "$(DATADIR)/{}" -name "*.xml" >> htr.index || [ -s htr.list ]

groundtruth.index: datadir
	echo "" > groundtruth.index
	cat "$(REPOROOT)/resources/werkvoorraad.csv" | grep -E ";GT" | awk -F ';' '{ print $$4"" }' | xargs -L 1 -I"{}" find "$(DATADIR)/{}" -name "*.xml" >> groundtruth.index || [ -s groundtruth.list ]

datadir:
ifeq ($(strip $(DATADIR)),)
	@echo "Usage Error: Data directory required, please specify a DATADIR=/path/to/datadir argument" >&2
	@exit 2
endif

checkdeps:
	which cut
	which find
	which awk
	which ucto
	which colibri-classencode
	which colibri-patternmodeller



