BIN:=../../src/crawler
PAP:=./papers

all:
	make init
	make ontology
	make gwas-catalog
	# make gwas-catalog snpedia

clean:
	-rm /tmp/gwas.sql

init:
	python $(BIN)/parse_gwas_catalog.py --init

snpedia:
	make -C ../associations/snpedia/

ontology:
	make -C ../ontology load-ontology

gwas-catalog: ../associations/gwas_catalog
	make -C $<
	python $(BIN)/parse_gwas_catalog.py \
	  --phenotypes $</trait_mappings.tsv \
	  --crawl $</gwas_catalog.tsv

# TODO: add parsing intructions
snpedia-associations:
	make -C ../associations/snpedia/

dl-papers:
	make -C ../papers open-access.txt
	python $(BIN)/dl_papers.py \
	  --mark-open-access ../papers/open-access.txt \
	  --download-oa $(PAP)

