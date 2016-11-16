PARSEDIR:=../../../src/crawler
PARSER:=$(PARSEDIR)/parse_efo_ontology.py
EFOURL:=http://data.bioontology.org/ontologies/EFO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv
FILTERS=./dispositions.txt ./measurement.txt ./phenotypes.txt ./biological-process.txt

load-ontology: ./efo.corrected.csv
	python $(PARSER) --csv $< --filters $(FILTERS)
	touch $@

clean:
	-rm efo.corrected.csv
	-rm /tmp/gwas.sql
	-rm load-ontology

efo.csv:
	wget "$(EFOURL)" -O $@.gz
	gunzip $@.gz

efo.corrected.csv: efo.csv
	cat $< | \
	  awk -v RS='"' 'NR % 2 == 0 { gsub(/\n/, "") } { printf("%s%s", $$0, "\"") }' | \
	  awk -v RS='"' 'NR % 2 == 0 { gsub(/,/, "~") } { printf("%s", $$0) }' \
	> $@.tmp
	mv $@.tmp $@

init:
	python $(PARSER) --init
