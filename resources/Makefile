REPOROOT := $(shell git rev-parse --show-toplevel)
RESOURCEDIR := $(REPOROOT)/resources/
EXPDIR := $(REPOROOT)/experiments/
DATADIR =

htr_corrections.json: ${EXPDIR}/htr_verbeterd_1.tsv $(REPOROOT)/scripts/process-htr-corrections.py
	python3 "$(REPOROOT)/scripts/process-htr-corrections.py"

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

locations_lexicon.lst: thesauri/locations/reconstructions.csv
	#Extract city/town names (and other locations)
	grep "http" "$<" | grep -v Amsteldam | cut -d "," -f 2 | sed '/^$$/d' | tr -d '"' | sort | uniq  > "$@" || (rm "$@" && false)

boedeltermen.autoexpanded.csv: boedeltermen.csv
	#Expands boedeltermen with variants found in the INT Historical Lexicon
	cp -f "$<" "$@" || (rm "$@" && false)
	"$(REPOROOT)/scripts/expandwithinthistlex.py" >> "$@" || (rm "$@" && false)

object_variants.tsv: boedeltermen.autoexpanded.csv
	#Curated object lexicon (variant list) from curated boedeltermen
	awk -F"," '($$2 == "voorwerp") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

object_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "voorwerp") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

occupation_variants.tsv: boedeltermen.autoexpanded.csv
	#Curated occupation lexicon (variant list) from curated boedeltermen
	awk -F"," '($$2 == "beroep") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

occupation_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "beroep") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

room_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "vertrek") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

room_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "vertrek") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

material_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "stofnaam") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

material_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "stofnaam") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

property_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "eigenschap") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

property_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "eigenschap") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

picture_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "voorstelling") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

picture_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "voorstelling") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

category_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "categorie") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

category_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "categorie") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

currency_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "munt") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

currency_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "munt") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

quantifier_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "eenheid") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

quantifier_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "eenheid") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

animal_variants.tsv: boedeltermen.autoexpanded.csv
	#from curated boedeltermen
	awk -F"," '($$2 == "dier") { print $$3"\t"$$4 }' < "$<" | "$(REPOROOT)/scripts/merge-tsv-rows.py" > "$@" || (rm "$@" && false)

animal_wordforms.lst: boedeltermen.autoexpanded.csv
	awk -F"," '($$2 == "dier") { print $$3"\n"$$4 }' < "$<" | sort | uniq > "$@" || (rm "$@" && false)

object_uncurated_lexicon.tsv:
	#Uncurated object lexicon (obsolete!)
	cut -d "," -f 1 "$(RESOURCEDIR)/objects.csv" | tr '[:upper:]' '[:lower:]' | tail --lines="+2" > "$@" || (rm "$@" && false)

keyword_uncurated_lexicon.tsv:
	#Keyword lexicon; keywords that may be indicative of an object (obsolete!)
	cut -d "," -f 1 "$(RESOURCEDIR)/keywords.csv" | tr '[:upper:]' '[:lower:]' > "$@" || (rm "$@" && false)

%.sanitized.tsv: %.tsv
	cd $(EXPDIR) && make groundtruth.tok.lexicon.tsv
	cd -
	sh -c 'TOPITEM=$$(head -n 1 $< | cut -f 1) TOPFREQ=$$(grep -e "^$$TOPITEM" $(EXPDIR)/groundtruth.tok.lexicon.tsv | sort -k2 -rn | head -n 1 | cut -f 2) $(REPOROOT)/scripts/sanitize_lexicon.py $< 5 $$TOPITEM $$TOPFREQ' > "$@" || (rm "$@" && false)

#Note: INT Historisch lexicon itself is not provided in this repo due to copyright restrictions, you need to get it yourself!
int_historisch_lexicon.wordforms.lst:
	#Extract wordforms from the INT historical lexicon
	cat "$(RESOURCEDIR)/int_historisch_lexicon.tsv" | awk '($$1 == "simple") { print $$7 }' | sort | uniq > "$@" || (rm "$@" && false)

int_historisch_lexicon.wordforms.freq.tsv: int_historisch_lexicon.wordforms.lst
	#Compute frequencies on the ground truth data for all INT Historical Lexicon wordforms
	cd $(EXPDIR) && make groundtruth.txt
	cd -
	lexmatch -M -l int_historisch_lexicon.wordforms.lst -t $(EXPDIR)/groundtruth.txt > "$@" || (rm "$@" && false)

int_historisch_lexicon_variants.tsv:
	#Extract a variant list from the INT historisch lexicon (without frequency information)
	"$(REPOROOT)/scripts/inthistlex2variantlist.py" int_historisch_lexicon.tsv > "$@" || (rm "$@" && false)

int_historisch_lexicon_variants.freq.tsv: int_historisch_lexicon.wordforms.freq.tsv
	#Extract a variant list from the INT historisch lexicon (with frequency information)
	"$(REPOROOT)/scripts/inthistlex2variantlist.py" int_historisch_lexicon.tsv int_historisch_lexicon.wordforms.freq.tsv > "$@" || (rm "$@" && false)

%_wordforms.freq.tsv: %_wordforms.lst
	cd $(EXPDIR) && make groundtruth.txt
	cd -
	lexmatch -M -l "$<" -t $(EXPDIR)/groundtruth.txt > "$@" || (rm "$@" && false)

countries.freq.tsv: lexicons/countries.lst
	cd $(EXPDIR) && make groundtruth.txt
	cd -
	lexmatch -f 0 -M -l "$<" -t $(EXPDIR)/groundtruth.txt | sed 's/\t0/\t1/' > "$@" || (rm "$@" && false)

regions.freq.tsv: lexicons/regions.lst
	cd $(EXPDIR) && make groundtruth.txt
	cd -
	lexmatch -f 0 -M -l "$<" -t $(EXPDIR)/groundtruth.txt | sed 's/\t0/\t1/' > "$@" || (rm "$@" && false)

%_lexicon.freq.tsv: %_lexicon.lst
	cd $(EXPDIR) && make groundtruth.txt
	cd -
	lexmatch -f 0 -M -l "$<" -t $(EXPDIR)/groundtruth.txt | sed 's/\t0/\t1/' > "$@" || (rm "$@" && false)

%_variants.freq.tsv: %_variants.tsv %_wordforms.freq.tsv
	#Enrich a variant list with frequency information
	"$(REPOROOT)/scripts/freqvariantlist.py" "$*_variants.tsv" "$*_wordforms.freq.tsv" > "$@" || (rm "$@" && false)

%_wordforms.freq.tsv: %_wordforms.lst
	cd $(EXPDIR) && make groundtruth.txt
	cd -
	lexmatch -M -l "$<" -t $(EXPDIR)/groundtruth.txt > "$@" || (rm "$@" && false)


.PHONY: all
all: first_names_lexicon.sanitized.tsv family_names_lexicon.sanitized.tsv streetnames_lexicon.tsv buildings_lexicon.tsv object_uncurated_lexicon.tsv int_historisch_lexicon_variants.tsv int_historisch_lexicon_variants.freq.tsv boedeltermen

.PHONY: boedeltermen
boedeltermen: object_variants.freq.tsv object_wordforms.freq.tsv property_variants.freq.tsv property_wordforms.freq.tsv material_variants.freq.tsv material_wordforms.freq.tsv picture_variants.freq.tsv picture_wordforms.freq.tsv category_variants.freq.tsv category_wordforms.freq.tsv room_variants.freq.tsv room_wordforms.freq.tsv currency_variants.freq.tsv currency_wordforms.freq.tsv animal_variants.freq.tsv animal_wordforms.freq.tsv quantifier_variants.freq.tsv quantifier_wordforms.freq.tsv

.PHONY: clean
clean:
	rm boedeltermen.autoexpanded.csv *_variants.tsv *.sanitized.tsv *_lexicon.tsv *.freq.tsv *.freq.lst *_wordforms* || true
	[ -e int_historisch_lexicon_2022_02_04.txt ] && ln -s int_historisch_lexicon_2022_02_04.txt int_historisch_lexicon.tsv

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
