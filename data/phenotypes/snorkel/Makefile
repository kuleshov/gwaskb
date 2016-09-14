PARSEDIR:=../../../src/crawler
PARSER:=$(PARSEDIR)/parse_snorkel_diseases.py
URL:=https://github.com/HazyResearch/snorkel/raw/master/tutorial/data/dicts.tar.gz

dicts:
	wget $(URL)
	tar -zxvf dicts.tar.gz

load-ontology: dicts
	python $(PARSER) \
	  --mesh $</CTD_diseases.tsv \
	  --chemicals $</mention_chemical.txt

init:
	python $(PARSER) --init
