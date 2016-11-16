GWASdb
------

GWASdb is a machine reading system for discovering associations between genetic mutations and disease from academic papers.

## Requirements

GWASdb is implemented in Python and requires:

* `lxml`, `ElementTree`
* `numpy`
* `sklearn`
* `sqlite`
* `snorkel`

Check out the Snorkel web page for a list of its requirements.

## Installation

To install GWASdb, clone this repo and set up your environement.

```
git clone https://github.com/kuleshov/gwasdb.git
cd gwasdb;
git submodule init;
git submodule update;

# now you must cd into ./snorkel-tables and follow snorkel's installation instructions!
cd ./snorkel-tables
./run.sh # this will install treedlib and the Stanford CoreNLP tools
cd ..

# finally, we setup the enviornment variables
source set_env.sh
```

Make sure all the required packages are installed. 
If a library is missing, `pip install --user <lib>` is the easiest way to install it.

## Datasets

We extract mutation/phenotype relations from the open-access subset of PubMed.

In addition, we use hand-curated databases such as GWAS Catalog and GWAS Central for evaluation, and we use various ontologies (EFO, SNOMED, etc.) for phenotype extraction.

The first step is to download this data onto your machine. The `data` subfolder contains code for doing this.

```
cd data/db

# we will store part of the dataset in a sqlite databset
make init # this will initialize an empty database

# next, we load a database of known phenotypes that might occur in the literature
# this will load phenotypes from the EFO ontology as well as 
# various ontologies collected by the Hazyresearch group
make phenotypes

# next, we download the contents of the hand-curated GWAS catalog database 
make gwas-catalog # loads into sqlite db (/tmp/gwas.sql by default); this takes a while

# now, let's download from pubmed all the open-access papers mentioned in the GWAS catalog
make dl-papers # downloads ~600 papers + their supplementary material!

# finally, we will use the GWAS central database for validation of the results
make gwas-central # this will only download the parts of GWAS central relevant to our papers
```

This process can be automated by just typing `make`.

## Information extraction

We demo our system in a series of Jupyter notebooks in the `notebooks` subfolder. 

1. `phenotype-extraction.ipynb` identifies the phenotypes studied in each paper
2. `table-pval-extraction.ipynb` extracts mutation ids and their associated p-values
3. `table-phenotype-extraction.ipynb` extracts relations between mutations and a specific phenotype (out of the many that can be described in the paper)
4. `acronym-extraction.ipynb`: often, phenotypes are mentioned via acronyms, and we need a module to resolve those acronyms
5. `evaluation.ipynb`: here, we merge all the results and evaluate our accuracy

The result is a second SQLite database containing facts (e.g. mutation/disease relations) that we have extracted from the literature.  

## Feedback

Please send feedback to [Volodymyr Kuleshov](http://web.stanford.edu/~kuleshov/).
