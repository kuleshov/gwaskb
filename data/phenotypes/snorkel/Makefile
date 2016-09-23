PARSEDIR:=../../../src/crawler
PARSER:=$(PARSEDIR)/parse_snorkel_diseases.py
URL:=https://github.com/HazyResearch/snorkel/raw/master/tutorial/data/dicts.tar.gz
SNOMED:= ./dicts/snomedct.disease_or_syndrome.txt ./dicts/snomedct.enzyme.txt ./dicts/snomedct.finding.txt ./dicts/snomedct.lab_procedure.txt ./dicts/snomedct.neoplastic_process.txt ./dicts/snomedct.proteins.txt ./dicts/snomedct.sign_or_symptom.txt

dicts:
	wget $(URL)
	tar -zxvf dicts.tar.gz

load-ontology: dicts
	python $(PARSER) \
	  --snomed $(SNOMED) \
	  # --mesh $</CTD_diseases.tsv \
	  # --chemicals $</mention_chemical.txt \

init:
	python $(PARSER) --init
