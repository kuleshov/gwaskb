import re

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

class KnowledgeBase():
  """Interface for accessing gold dataset and extracted facts"""

  def __init__(self):
    pass

  # ----------------------------------------------------------------------------
  # database lookup

  def paper_by_pmid(self, pmid):
    return db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()

  def rsids_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return [str(assoc.snp.rs_id) for assoc in paper.associations]

  def pvals_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return [assoc.pvalue for assoc in paper.associations]

  def phen_names_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return set (
      [ _clean_phenotype(assoc.phenotype.name) for assoc in paper.associations ] + 
      [ syn.lower() for assoc in paper.associations for syn in assoc.phenotype.synonyms.split('|') 
        if assoc.phenotype.ontology_ref ]
    )

  def phen_by_pmid(self, pmid, source='efo'):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    first_degree_phens = [ assoc.phenotype for assoc in paper.associations 
                           if assoc.phenotype.source == source ]
    second_degree_phens = [ eqphen for assoc in paper.associations
                                   for eqphen in assoc.phenotype.equivalents
                                   if eqphen.source == source ]
    return set(first_degree_phens + second_degree_phens)

  def title_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return paper.title

  def assoc_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    return paper.associations

  # ----------------------------------------------------------------------------
  # candidate extraction

  def get_rsid_candidates(self):
    """Returns list of valid rs-ids"""
    candidates = db_session.query(SNP.rs_id).all()
    candidates = [str(c[0]) for c in candidates if re.match(r'^rs\d+$', c[0])]
    return candidates

  def get_phenotype_candidates(self, mod_fn=lambda x: x.lower()):
    """Returns dictionary of phenotype candidates

    Outputs all phenotypes described in gwas_catalog, plus their EFO mappings
    """
    phenotypes = db_session.query(Phenotype).filter(Phenotype.source=='efo').all()
    phenotype_names = set()
    for phenotype in phenotypes:
      if phenotype.name:
        phenotype_names.add(mod_fn(phenotype.name))
      synonyms = [mod_fn(syn) for syn in phenotype.synonyms.split('|')]
      phenotype_names.update(synonyms)

    return list(phenotype_names)

  def get_phenotype_candidates_cheating(self, mod_fn=lambda x: x.lower()):
    """Returns dictionary of phenotype candidates

    Outputs all phenotypes described in gwas_catalog, plus their EFO mappings
    """
    associations = db_session.query(Association).all()
    phenotype_names = set()
    for association in associations:
      phenotypes = association.phenotype.equivalents
      for phenotype in phenotypes:
        if phenotype.name:
          phenotype_names.add(mod_fn(phenotype.name))
        synonyms = [mod_fn(syn) for syn in phenotype.synonyms.split('|')]
        phenotype_names.update(synonyms)

    return list(phenotype_names)

# ----------------------------------------------------------------------------
# helpers

def _clean_phenotype(text):
  text = text.lower()
  text = re.sub(r'\([^)]*\)', '', text)
  fields = text.split()
  text = ' '.join(fields)
  return text