import argparse

from sqlalchemy.sql import exists, and_, or_

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

open_access_papers = db_session.query(Paper).filter(Paper.open_access==True).all()
assocs = [assoc for paper in open_access_papers for assoc in paper.associations ]
a_tuples = [(a.phenotype.name, a.paper_id, a.snp_id) for a in assocs]

print 'open access papers:', len(open_access_papers)
print 'open associaitons:', len(set(a_tuples))
print 'all papers:', db_session.query(Paper).count()
print 'all associaitons:', db_session.query(Association).count()

print 'conservative:'
a_tuples = [(a.paper_id, a.snp_id) for a in assocs]

print 'open access papers:', len(open_access_papers)
print 'open associaitons:', len(set(a_tuples))
print 'all papers:', db_session.query(Paper).count()
print 'all associaitons:', db_session.query(Association).count()