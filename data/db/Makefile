BIN:=../../src/crawler
PAP:=./papers

all:
	make init
	make ontology
	make gwas-catalog
	make gwas-central
	# make gwas-catalog snpedia

clean:
	-rm /tmp/gwas.sql

init:
	python $(BIN)/parse_gwas_catalog.py --init

snpedia:
	make -C ../associations/snpedia/

phenotypes:
	# make -C ../phenotypes/efo load-ontology
	make -C ../phenotypes/snorkel load-ontology

gwas-catalog: ../associations/gwas_catalog
	make -C $<
	python $(BIN)/parse_gwas_catalog.py \
	  --phenotypes $</trait_mappings.tsv \
	  --crawl $</gwas_catalog.tsv

gwas-central: first-15-paper-ids.txt
	python $(BIN)/parse_gwas_central.py \
		--ids $< \
		--min-neg-log-pval 1

first-15-paper-ids.txt:
	  ls $(PAP) | grep xml | cut -f 1 -d '.' | head -n 15 > $@

# TODO: add parsing intructions
snpedia-associations:
	make -C ../associations/snpedia/

dl-papers:
	make -C ../papers open-access.txt
	python $(BIN)/dl_papers.py \
	  --mark-open-access ../papers/open-access.txt \
	  --download-oa $(PAP)

