import re

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

class KnowledgeBase():
  """Interface for accessing gold dataset and extracted facts"""

  def __init__(self):
    pass

  def get_rsid_candidates(self):
    """Returns list of valid rs-ids"""
    candidates = db_session.query(SNP.rs_id).all()
    candidates = [str(c[0]) for c in candidates if re.match(r'^rs\d+$', c[0])]
    return candidates

  def get_phenotype_candidates(self):
    """Returns dictionary of phenotype candidates

    Outputs all phenotypes described in gwas_catalog, plus their EFO mappings
    """
    phenotypes = db_session.query(Phenotype).filter(Phenotype.source=='gwas_catalog').all()
    phenotype_names = set()
    for phenotype in phenotypes:
      if phenotype.name:
        phenotype_names.add(phenotype.name.lower())
      if phenotype.ontology_ref:
        phenotype_names.add(phenotype.ontology_ref.lower())

    return list(phenotype_names)

  def rsids_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return [str(assoc.snp.rs_id) for assoc in paper.associations]

  def pvals_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return [assoc.pvalue for assoc in paper.associations]

  def phens_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return [assoc.phenotype.name.lower() for assoc in paper.associations] \
         + [assoc.phenotype.ontology_ref.lower() for assoc in paper.associations if assoc.phenotype.ontology_ref]

