# Overview of Results

This document describes the output of GwasKB.

## Associations

The main output of GwasKB is a set of associations, which are triples `(variant, phenotype, p-value)`.

The following files contain the association extracted by GwasKB from a set of 589 open-access GWAS papers.

* `notebooks/results/associations.tsv`: complete list of associations extracted by the system
* `notebooks/results/associations.known.tsv`: subset of associations confirmed in the GWAS Catalog or GWAS Central
* `notebooks/results/associations.new.tsv`: subset of associations not found in the GWAS Catalog or GWAS Central
* `notebooks/results/associations.annotated.tsv`: associations annotated with their location in the original paper (table, row, column)

## Additional Files

GwasKB also generates several additional files.

### Auxiliary Extracted Files

The main ouptut found is `associations.tsv` is created in the `evaluation.ipynb` notebook from a set of input files that come out of the different GwasKB modules (e.g., phenotype module, p-value extraction module, etc).

These are the individual input files that go into making the output.

* `notebooks/results/nb-output/acronyms.extracted.all.tsv`: List of acronyms extracted for each paper. Rows are: `pmid`, `phenotype`, `acronym`. We use these downstream to resolve acronyms.
* `notebooks/results/nb-output/phen-rsid.table.rel.all.tsv`: List of `pmid/rsid/phenotype` triples. These are detailed phenotypes extracted from tables for specific `rsid`'s. Each row is also tagged with the table, row, and column numbers that indicate where the `rsid` was found.
* `notebooks/results/nb-output/phenotypes.extracted.tsv`: List of simple phenotypes extracted for each paper. Each phenotype is a set of up to 3 keywords separated by `|`.
* `notebooks/results/nb-output/pval-rsid.filtered.tsv`: List of `pmid/rsid/log10(p-value)` triples. Each row is also tagged with the table, row, and column numbers that indicate where the `rsid` was found.
* `notebooks/results/nb-output/rsids.singletons.all.tsv`: List of singleton `rsids` that were found in tables, but did not have an associated p-value.

### Files for Evaluation

* `notebooks/results/util/associations.gwcat.tsv` : List of `pmid/rsid/phenotype/log10(p-value)` representing associations found in the Gwas Catalog.
* `notebooks/results/util/associations.gwcen.tsv` : List of `pmid/rsid/phenotype/log10(p-value)` representing associations found in the Gwas Central.
* `notebooks/results/util/phenotype.mapping.annotated.tsv` : Mapping of Gwas Central phenotypes to GwasKB phenotypes. The columns are: Gwas Central phenotype, simple GwasKB phenotype, detailed GwasKB phenotype, code. The code is: 0=incorrect phenotype, 1=incorrect because acronym was not resolved, 2=approximately correct, 3=fully correct.
* `notebooks/results/util/phenotype.mapping.gwascat.annotated.tsv` : Mapping of Gwas Catalog phenotypes to GwasKB phenotypes. The columns are: Gwas Catalog phenotype, simple GwasKB phenotype, detailed GwasKB phenotype, code. The code is: 0=incorrect phenotype, 1=incorrect because acronym was not resolved, 2=approximately correct, 3=fully correct.
* `notebooks/results/util/rels.discovered.annotated.txt` : 100 random new relations and our annotations.

## Input

The publications used to generate the above results can be downloaded from `https://stanford.app.box.com/s/w0etl89129gxt2l2amoo7u936511fhy5`.
