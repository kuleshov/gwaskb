# Overview of Results

This document describes the output of GwasKB.

## Associations

The main output of GwasKB is a set of associations, which are triples `(variant, phenotype, p-value)`.

The following files contain the associations extracted by GwasKB from a set of 589 open-access GWAS papers.

* `notebooks/results/associations.tsv`: complete list of associations extracted by the system
* `notebooks/results/associations.known.tsv`: subset of associations confirmed in the GWAS Catalog or GWAS Central
* `notebooks/results/associations.new.tsv`: subset of associations not found in the GWAS Catalog or GWAS Central

## Additional Files

GwasKB also generates several additional files.

### Mapping Between GwasKB Output and Original Papers

In order to make it easier to reproduce our results, we report a mapping between the entities extracted by GwasKB (e.g., p-values) and the locations in the original papers where they are found. 

A GwasKB association is a triple of `(variant, phenotype, p-value)`. For each of these three entities, we provide a file that points to a location in a paper from which this variant was identified. The following files contain these mappings.

Note that these files are loaded by our last (analysis) notebook. The code for combining them into the final associations is in that notebook.

* `notebooks/results/nb-output/pval-rsid.filtered.tsv`: File containing the p-values and the variants (identfied by their `rsid`) extracted by our system. Specifically, each row contains the paper `pmid`, variant `rsid`, table number, row number, column number that indicate where the `rsid` was found, and finally the `log10(p-value)`. The p-value is always found in the same row as the `rsid`.
* `notebooks/results/nb-output/phen-rsid.table.rel.all.tsv`: this file contains precise phenotypes for variants. The first three columns are the Pubmed ID of the paper, the RSID of the variant, the phenotype that we identified for that variant. The last three columns also include the table, row, and column numbers that indicate where the `rsid` was found.
* `notebooks/results/nb-output/phenotypes.extracted.tsv`: this file contains the simple phenotype identified for each paper. The colums are the Pubmed ID of the paper, and the phenotype that we identified. Each phenotype is a set of up to 3 keywords separated by `|`.
* `notebooks/results/nb-output/acronyms.extracted.all.tsv`: Sometimes, precise phenotypes are reported as acronyms. This file contains the mapping that we extracted to resolve these acronyms. The columns are: `pmid`, `phenotype`, `acronym`.
* `notebooks/results/nb-output/rsids.singletons.all.tsv`: List of singleton `rsids` that were found in tables, but did not have an associated p-value.

### Notebooks For Reproducing Our Biological Analysis

* Chris's notebooks.

### Additional Metadata

* Braden p-values

### Files Used For Evaluating GwasKB

We used the following files in order to analyze the output of our system.

* `notebooks/results/util/associations.gwcat.tsv` : List of `pmid/rsid/phenotype/log10(p-value)` representing associations found in the Gwas Catalog.
* `notebooks/results/util/associations.gwcen.tsv` : List of `pmid/rsid/phenotype/log10(p-value)` representing associations found in the Gwas Central.
* `notebooks/results/util/phenotype.mapping.annotated.tsv` : Mapping of Gwas Central phenotypes to GwasKB phenotypes. The columns are: Gwas Central phenotype, simple GwasKB phenotype, detailed GwasKB phenotype, code. The code is: 0=incorrect phenotype, 1=incorrect because acronym was not resolved, 2=approximately correct, 3=fully correct.
* `notebooks/results/util/phenotype.mapping.gwascat.annotated.tsv` : Mapping of Gwas Catalog phenotypes to GwasKB phenotypes. The columns are: Gwas Catalog phenotype, simple GwasKB phenotype, detailed GwasKB phenotype, code. The code is: 0=incorrect phenotype, 1=incorrect because acronym was not resolved, 2=approximately correct, 3=fully correct.
* `notebooks/results/util/rels.discovered.annotated.txt` : 100 random new relations and our annotations.

## Input Used By GwasKB To Generate Results

The publications used to generate the above results can be downloaded from `https://stanford.app.box.com/s/w0etl89129gxt2l2amoo7u936511fhy5`.

