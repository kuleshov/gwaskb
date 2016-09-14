"""Load and parse EFO ontology into database

This parse the EFO csv file into Phenotype objects.
  name: receives the main EFO name
  synonyms: join of synonyms on '|'
  source: 'efo'
  ontology_ref: the EFO id
"""

import re
import argparse
import string
import unicodedata

from sqlalchemy.sql import exists, and_, or_

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--init', action='store_true', help='Init db')
  parser.add_argument('--file', help='Load phenotypes')
  args = parser.parse_args()

  if args.init:
    init_db()

  if args.file:
    parse_ontology(args.file, db_session)

def parse_ontology(fname, db_session):
  with open(fname) as f:
    for line in f:
      fields = line.strip().split(',')
      name = _normalize_str(fields[1])
      name = re.sub('"', '', name)

      phenotype = Phenotype(
                    name=name,
                    source='snorkel',
                  )

      db_session.add(phenotype)
  
  db_session.commit()

def _normalize_str(s):
  s = s.replace("\"", "") # remove quotes
  s = s.decode('utf-8')
  s = unicodedata.normalize('NFKD', s).encode('ascii','ignore')
  # print s
  return s
  # return unicode(s)


# ----------------------------------------------------------------------------

if __name__ == '__main__':
  main()