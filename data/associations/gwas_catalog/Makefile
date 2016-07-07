DATABASEURL:=https://www.ebi.ac.uk/gwas/api/search/downloads/full
TRAITMAPURL:=https://www.ebi.ac.uk/gwas/api/search/downloads/trait_mappings

all:
	make gwas_catalog.tsv trait_mappings.tsv

gwas_catalog.tsv:
	wget $(DATABASEURL) -O $@.tmp
	mv $@.tmp $@

trait_mappings.tsv:
	wget $(TRAITMAPURL) -O $@.tmp
	mv $@.tmp $@
