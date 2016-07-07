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
  parser.add_argument('--phenotypes', help='Load phenotype/ontology mapping')
  parser.add_argument('--crawl', help='Start crawl; parse .tsv file')

  args = parser.parse_args()

  if args.init:
    init_db()

  if args.phenotypes:
    phenotypes(args.phenotypes, db_session)

  if args.crawl:
    crawl(args.crawl, db_session)

def phenotypes(fname, db_session):
  phenotypes = set()
  with open(fname) as f:
    f.readline()
    for line in f:
      fields = line.split('\t')
      reported_phenotype = _normalize_str(fields[0])
      ontology_phenotype = _normalize_str(fields[1])
      ontology_id = fields[2]

      if reported_phenotype not in phenotypes:
        db_session.add(
          Phenotype(
            name=reported_phenotype,
            source='gwas_catalog',
            synonyms=ontology_phenotype,
            ontology_ref=ontology_id
          )
        )
        phenotypes.add(reported_phenotype)
  
  db_session.commit()

def crawl(fname, db_session):
  with open(fname) as f:
    f.readline()
    for line in f:
      fields = line.split('\t')

      # create paper
      pubmed_id = _get_int(fields[1])
      journal_name = fields[4]
      title = _normalize_str(fields[6])

      paper = db_session.query(Paper).filter(Paper.pubmed_id==pubmed_id).first()
      if not paper:
        paper = Paper(pubmed_id=pubmed_id, title=title, journal=journal_name)
        db_session.add(paper)
        db_session.commit()

      # create snp
      chrom = _get_chrom(fields[11])
      pos = _get_int(fields[12])
      rs_id = fields[21]

      snp = db_session.query(SNP).filter(SNP.rs_id==rs_id).first()
      if not snp:
        snp = SNP(chrom=chrom, position=pos, rs_id=rs_id)
        db_session.add(snp)
        db_session.commit()

      # create phenotype
      phenotype_name = _normalize_str(fields[7])
      phenotype = db_session.query(Phenotype).filter(and_(
                    Phenotype.name==phenotype_name,
                    Phenotype.source=='gwas_catalog',
                  )).first() # max 1 phenotype from gwas_catalog
      if not phenotype:
        phenotype = Phenotype(name=phenotype_name, source='gwas_catalog')
        db_session.add(phenotype)
        db_session.commit()

      # create association
      n_cases = _get_single_digit(fields[8])
      n_controls = _get_single_digit(fields[9])
      pop = fields[8] + ' ' + fields[9]
      freq = _get_float(fields[26])
      pvalue = _get_float(fields[28])
      oddsratio, beta = _get_or(fields[30], fields[31])
      allele = _get_allele(fields[18])

      db_session.add(Association(
        snp=snp,
        phenotype=phenotype,
        paper=paper,
        freq=freq,
        pvalue=pvalue,
        oddsratio=oddsratio,
        beta=beta,
        allele=allele,
        source='gwas_central'
      ))

      db_session.commit()

# ----------------------------------------------------------------------------
# parsing

def _normalize_str(s):
  s = s.decode('utf-8')
  return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
  # return unicode(s)

def _get_digits(s):
  tokens = s.split()

  table = string.maketrans("","")
  tokens = [t.translate(table, string.punctuation) for t in tokens]

  digits = [int(t) for t in tokens if t.isdigit()]
  return digits

def _get_single_digit(s):
  digits = _get_digits(s)
  if len(digits) == 1:
    return digits[0]
  else:
    return None

def _get_allele(s):
  fields = s.split('-')
  if len(fields) == 2:
    if all(f in ('A', 'T', 'C', 'G', '?') for f in fields[1]):
      return fields[1]
  return None

def _get_or(s1, s2):
  if not s1 or not s2: return None, None
  if s2[-1] == ']':
    oddsratio = float(s1) if s1 else None
    beta = None
  else:
    oddsratio = None
    beta = float(s1) if s1 else None
  return oddsratio, beta

def _get_float(s):
  try:
    f = float(s)
  except ValueError:
    f = None
  return f

def _get_int(s):
  try:
    i = int(s)
  except ValueError:
    i = None
  return i  

def _get_chrom(s):
  if s == 'X':
    x = 23
  else:
    x = _get_int(s)
  return x

# ----------------------------------------------------------------------------

if __name__ == '__main__':
  main()