REPOROOT := $(shell git rev-parse --show-toplevel)
RESOURCEDIR := $(REPOROOT)/resources/
EXPDIR := $(REPOROOT)/experiments/
DATADIR =

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
	cut -d "," -f 3 $< | sed '/^$$/d' | grep -ivE "^van$$" | tail --lines="+2" |  sort | uniq -c | sort -rn | awk '{first=$$1; $$1=""; gsub(/^[ \t]+/, "", $$0); if (length($$0) >= 3 && first > 1) { print $$0"\t"first } }' | grep -v " " | grep -v "\." | grep -v ":" | grep -v "@" > "$@" || (rm "$@" && false)

family_names_lexicon.tsv: personnamesNA.csv
	#Extract last names
	cut -d "," -f 4,5 $< | tr "," " " | sed '/^\s*$$/d' | grep -ivE "^van$$" | tail --lines="+2" | sort | uniq -c | sort -rn | awk '{first=$$1; $$1=""; gsub(/^[ \t]+/, "", $$0); if (length($$0) >= 3 && first > 1) { print $$0"\t"first } }' | grep -v " " | grep -v "\." | grep -v ":" | grep -v "@" > "$@" || (rm "$@" && false)

streetnames_lexicon.tsv: streetnamesAdamlink.csv
	#Extract street names
	cut -d "," -f 2  $< | sed '/^$$/d' | tr -d '"' | sort | uniq  > "$@" || (rm "$@" && false)

buildings_lexicon.tsv: buildingsAdamlink.csv
	#Extract street names
	cut -d "," -f 2  $< | sed '/^$$/d' | tr -d '"' | sort | uniq  > "$@" || (rm "$@" && false)

object_variants.tsv: boedeltermen.csv
	#Curated object lexicon (variant list) from curated boedeltermen
	awk -F"," '($$2 == "voorwerp") { print $$3"\t"$$4 }' < boedeltermen.csv | "$(REPOROOT)/scripts/merge-tsv-rows.py" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

room_variants.tsv: boedeltermen.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "vertrek") { print $$3"\t"$$4 }' < boedeltermen.csv | "$(REPOROOT)/scripts/merge-tsv-rows.py" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

material_variants.tsv: boedeltermen.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "stofnaam") { print $$3"\t"$$4 }' < boedeltermen.csv | "$(REPOROOT)/scripts/merge-tsv-rows.py" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

property_variants.tsv: boedeltermen.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "eigenschap") { print $$3"\t"$$4 }' < boedeltermen.csv | "$(REPOROOT)/scripts/merge-tsv-rows.py" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

picture_variants.tsv: boedeltermen.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "voorstelling") { print $$3"\t"$$4 }' < boedeltermen.csv | "$(REPOROOT)/scripts/merge-tsv-rows.py" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

category_variants.tsv: boedeltermen.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "categorie") { print $$3"\t"$$4 }' < boedeltermen.csv | "$(REPOROOT)/scripts/merge-tsv-rows.py" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

currency_variants.tsv: boedeltermen.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "munt") { print $$3"\t"$$4 }' < boedeltermen.csv | "$(REPOROOT)/scripts/merge-tsv-rows.py" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

object_lexicon.tsv:
	#Uncurated object lexicon
	cut -d "," -f 1 "$(RESOURCEDIR)/objects.csv" | tr '[:upper:]' '[:lower:]' | tail --lines="+2" > "$@" || (rm "$@" && false)

keyword_lexicon.tsv:
	#Keyword lexicon; keywords that may be indicative of an object
	cut -d "," -f 1 "$(RESOURCEDIR)/keywords.csv" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

sanitized_first_names_lexicon.tsv: first_names_lexicon.tsv
	"$(REPOROOT)/scripts/sanitize_lexicon.py" $< > "$@" || (rm "$@" && false)


sanitized_family_names_lexicon.tsv: family_names_lexicon.tsv
	"$(REPOROOT)/scripts/sanitize_lexicon.py" $< > "$@" || (rm "$@" && false)

#Note: INT Historisch lexicon itself is not provided in this repo due to copyright restrictions, you need to get it yourself!
int_historisch_lexicon.wordforms.lst:
	#Extract wordforms from the INT historical lexicon
	cat "$(RESOURCEDIR)/int_historisch_lexicon.tsv" | awk '($$1 == "simple") { print $$7 }' | sort | uniq > "$@" || (rm "$@" && false)

int_historisch_lexicon.wordforms.freq.tsv: int_historisch_lexicon.wordforms.lst
	#Compute frequencies on the ground truth data for all INT Historical Lexicon wordforms
	cd $(EXPDIR) && make groundtruth.txt
	cd -
	lexmatch -M -l int_historisch_lexicon.wordforms.lst -t $(EXPDIR)/groundtruth.txt > "$@" || (rm "$@" && false)

int_lemma_hist_variants.tsv: int_historisch_lexicon.wordforms.freq.tsv
	#Extract a variant list from the INT historisch lexicon
	"$(REPOROOT)/scripts/inthistlex2variantlist.py" int_historisch_lexicon.tsv int_historisch_lexicon.wordforms.freq.tsv > "$@" || (rm "$@" && false)


.PHONY: all
all: sanitized_first_names_lexicon.tsv sanitized_family_names_lexicon.tsv streetnames_lexicon.tsv buildings_lexicon.tsv object_lexicon.tsv int_lemma_hist_variants.tsv

.PHONY: boedeltermen
boedeltermen: object_variants.tsv property_variants.tsv material_variants.tsv picture_variants.tsv category_variants.tsv room_variants.tsv currency_variants.tsv

.PHONY: clean
clean:
	rm *_variants.tsv sanitized_*.tsv object_lexicon.tsv *_lexicon.tsv

.PHONY: checkdeps
checkdeps:
	which cut
	which find
	which awk
	which ucto
	which lexmatch
	python3 -c 'import SPARQLWrapper'
	python3 -c 'import pandas'

.PHONY: help
help:
	@cat README.md
