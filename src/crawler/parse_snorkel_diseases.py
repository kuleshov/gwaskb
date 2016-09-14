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
  parser.add_argument('--mesh', help='Mesh diseases')
  parser.add_argument('--chemicals', help='Mesh chemicals')
  args = parser.parse_args()

  if args.init:
    init_db()

  if args.mesh:
    parse_mesh(args.mesh, db_session)

  if args.chemicals:
    parse_chemicals(args.chemicals, db_session)  

def parse_mesh(fname, db_session):
  with open(fname) as f:
    for line in f:
      if line.startswith('#'): continue
      
      fields = line.strip().split('\t')
      if len(fields) < 8: continue

      name = _normalize_str(fields[0])
      ontology_id = fields[1]
      synonyms = _normalize_str(fields[7].lower())

      phenotype = Phenotype(
                    name=name,
                    source='mesh',
                    synonyms=synonyms,
                    ontology_ref=ontology_id
                  )

      db_session.add(phenotype)
  
  db_session.commit()

def parse_chemicals(fname, db_session):
  with open(fname) as f:
    for line in f:
      if line.startswith('#'): continue
      
      fields = line.strip().split('\t')

      name = _normalize_str(fields[0])
      ontology_id = fields[1]

      phenotype = Phenotype(
                    name=name,
                    source='chemical',
                    ontology_ref=ontology_id
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