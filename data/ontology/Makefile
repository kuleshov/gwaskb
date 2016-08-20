PARSEDIR:=../../src/crawler
PARSER:=$(PARSEDIR)/parse_efo_ontology.py
EFOURL:=http://data.bioontology.org/ontologies/EFO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv

load-ontology: ./efo.corrected.csv
	python $(PARSER) --csv $<

efo.csv:
	wget "$(EFOURL)" -O $@.gz
	gunzip $@.gz

efo.corrected.csv: efo.csv
	cat $< | \
	  grep 'EFO_' | \
	  tr '\n' '\r' | \
	  awk -v RS='"' 'NR % 2 == 0 { gsub(/\r/, "") } { printf("%s%s", $$0, RT) }' | \
	  tr '\r' '\n' \
	> $@.tmp
	mv $@.tmp $@

init:
	python $(PARSER) --init
