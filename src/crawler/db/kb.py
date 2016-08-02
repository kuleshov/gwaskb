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

  def rsids_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    assocs = db_session.query(Association).filter(Association.paper==paper).all()
    return [str(assoc.snp.rs_id) for assoc in paper.associations]

  def pvals_by_pmid(self, pmid):
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    assocs = db_session.query(Association).filter(Association.paper==paper).all()
    return [assoc.pvalue for assoc in paper.associations]

