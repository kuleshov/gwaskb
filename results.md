# Overview of Results

This document describes the output of GwasKB.

## Associations

The main output of GwasKB is a set of associations, which are triples `(variant, phenotype, p-value)`.

In our paper, we performed machine curation on  589 open-access GWAS papers and have selected and analyzed a set of associations that strikes a good tradeoff between precision and recall of the machine curation system.

The following files contain these associations:

* `notebooks/results/associations.tsv`: complete list of associations extracted by the system
* `notebooks/results/associations.known.tsv`: subset of associations confirmed in the GWAS Catalog or GWAS Central
* `notebooks/results/associations.new.tsv`: subset of associations not found in the GWAS Catalog or GWAS Central

## Additional Files

GwasKB also generates several additional files.

### Intermediary Outputs

Our system is implemented in a series of Jupyter notebooks, each running a module of the system. 

Each module is responsible for extracting one type of data element (e.g. p-values). These intermediary outputs are recorded in the `nb-output` folder. The final notebook collects these outputs to form our final list of associations.

In each row of each intermediary output file (e.g. for each p-value), we provide coordinates that point to a location in a paper where that data element (e.g. the p-value) was found. 

The following files are the intermediary outputs; they also contain the coordinates of the extracted data elements.

* `notebooks/results/nb-output/pval-rsid.filtered.tsv`: File containing the p-values and the variants (identfied by their `rsid`) extracted by our system. Specifically, each row contains the paper `pmid`, variant `rsid`, table number, row number, column number that indicate where the `rsid` was found, and finally the `log10(p-value)`. The p-value is always found in the same row as the `rsid`.
* `notebooks/results/nb-output/p-values.tsv`: File containing the p-values extracted by GwasKB and their location within publications (represented by a paper pubmed id, a table id, and a row, column coordinate).
* `notebooks/results/nb-output/phen-rsid.table.rel.all.tsv`: this file contains precise phenotypes for variants. The first three columns are the Pubmed ID of the paper, the RSID of the variant, the phenotype that we identified for that variant. The last three columns also include the table, row, and column numbers that indicate where the `rsid` was found.
* `notebooks/results/nb-output/phenotypes.extracted.tsv`: this file contains the simple phenotype identified for each paper. The colums are the Pubmed ID of the paper, and the phenotype that we identified. Each phenotype is a set of up to 3 keywords separated by `|`.
* `notebooks/results/nb-output/acronyms.extracted.all.tsv`: Sometimes, precise phenotypes are reported as acronyms. This file contains the mapping that we extracted to resolve these acronyms. The columns are: `pmid`, `phenotype`, `acronym`.
* `notebooks/results/nb-output/rsids.singletons.all.tsv`: List of singleton `rsids` that were found in tables, but did not have an associated p-value.

Note that these files are loaded by our last (analysis) notebook. The code for combining them into the final associations is in that notebook.

### Notebooks For Reproducing Our Biological Analysis

The following notebooks can be used to reproduce the biological analysis of the set of "novel" variants identified by GwasKB.

* `notebooks/bio-analysis/enrichment/enrichment.ipynb`: this notebook reproduces the enrichment analysis of GwasKB variants associated with either auto-immune or neuro-degenerative diseases.
* `notebooks/bio-analysis/effect-sizes/effect-sizes.ipynb`: this notebook reproduces the analysis of the effect sizes of variants identified by GwasKB.

### Additional Metadata

The following files contain additional meta-data that complements our main results.

* `notebooks/results/metadata/pvalue_metadata.tsv`: meta-data extracted for each p-value that we report.
* `notebooks/results/metadata/pval-rsid.metadata.tsv`: meta-data extracted for each (rsid, p-value) tuple that we report. Note that the format of this file is the same as that of the `pval-rsid` file produced by our system and that is found in `nb-output`. We obtain this file my mapping the above p-value metadata to the rsid's that were found to be associated with these p-values.
* `notebooks/results/metadata/GWAS_pvalue_headers.ipynb`: Notebook for extracting the above metadata.
* `./results.md`: Document describing all the files that are released together with GwasKB.

### Files Used For Evaluating GwasKB

We used the following files in order to analyze the output of our system.

* `notebooks/results/util/associations.gwcat.tsv` : List of `pmid/rsid/phenotype/log10(p-value)` representing associations found in the Gwas Catalog.
* `notebooks/results/util/associations.gwcen.tsv` : List of `pmid/rsid/phenotype/log10(p-value)` representing associations found in the Gwas Central.
* `notebooks/results/util/phenotype.mapping.annotated.tsv` : Mapping of Gwas Central phenotypes to GwasKB phenotypes. The columns are: Gwas Central phenotype, simple GwasKB phenotype, detailed GwasKB phenotype, code. The code is: 0=incorrect phenotype, 1=incorrect because acronym was not resolved, 2=approximately correct, 3=fully correct.
* `notebooks/results/util/phenotype.mapping.gwascat.annotated.tsv` : Mapping of Gwas Catalog phenotypes to GwasKB phenotypes. The columns are: Gwas Catalog phenotype, simple GwasKB phenotype, detailed GwasKB phenotype, code. The code is: 0=incorrect phenotype, 1=incorrect because acronym was not resolved, 2=approximately correct, 3=fully correct.
* `notebooks/results/util/rels.discovered.annotated.txt` : 100 random new relations and our annotations.

## Input Data Used By GwasKB To Generate Results

The publications used to generate the above results can be downloaded from `https://stanford.app.box.com/s/w0etl89129gxt2l2amoo7u936511fhy5`.

