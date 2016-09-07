SRC:=../../../src/crawler
PAPERS:=../../db/papers

init:
	python $(SRC)/parse_gwas_central.py --init

run: first-15-paper-ids.txt
	python $(SRC)/parse_gwas_central.py \
	  --ids $< \
	  --min-neg-log-pval 5

first-15-paper-ids.txt:
	ls $(PAPERS) | grep xml | cut -f 1 -d '.' | head -n 15 > $@
