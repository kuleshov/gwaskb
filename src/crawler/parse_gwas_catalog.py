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
  parser.add_argument('--phenotypes', help='Phenotype/ontology mapping')
  parser.add_argument('--crawl', help='Start crawl; parse .tsv file')

  args = parser.parse_args()

  if args.init:
    init_db()

  if args.crawl:
    crawl(args.crawl, args.phenotypes, db_session)

def load_phenotypes(fname, db_session):
  """Load phenotype name -> efo_id list"""
  phen2id = dict()
  with open(fname) as f:
    f.readline()
    for line in f:
      fields = line.split('\t')
      reported_phenotype = _normalize_str(fields[0].lower())
      ontology_phenotype = _normalize_str(fields[1])
      ontology_id = fields[2]

      if reported_phenotype not in phen2id:
        phen2id[reported_phenotype] = ontology_id
      else:
        # raise Exception('Same phenotype maps to two EFO ids')
        print 'WARNING: Phenotype "%s" maps to multiple EFO ids: %s, %s' % \
              (reported_phenotype, ontology_id, phen2id[reported_phenotype])
        

  return phen2id

def crawl(fname, phenotype_fname, db_session):
  phen2id = load_phenotypes(phenotype_fname, db_session)

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
      ref = 'GRCh38'

      snp = db_session.query(SNP).filter(SNP.rs_id==rs_id).first()
      if not snp:
        snp = SNP(chrom=chrom, position=pos, rs_id=rs_id)
        db_session.add(snp)
        db_session.commit()

      # create phenotype
      phenotype_name = _normalize_str(fields[7].lower())
      if phenotype_name in phen2id:
        efo_id = phen2id[phenotype_name]
        phenotypes = db_session.query(Phenotype).filter(and_(
                      Phenotype.ontology_ref==efo_id,
                      Phenotype.source=='efo',
                    )).all()
        if len(phenotypes) != 1:
          print [(p.name, p.ontology_ref) for p in phenotypes]
          raise Exception('Could not find unique phenotype entry for %s (%s)'
                          % (phenotype_name, efo_id))
        else:
          phenotype = phenotypes[0]
      else:
        phenotype = Phenotype(name=phenotype_name, source='gwas_catalog')
        db_session.add(phenotype)
        db_session.commit()

      # create association
      n_cases = _get_single_digit(fields[8])
      n_controls = _get_single_digit(fields[9])
      pop = fields[8] + ' ' + fields[9]
      freq = _get_float(fields[26])
      pvalue = _get_float(fields[27])
      beta_params = _normalize_str(fields[31])
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
        beta_params=beta_params,
        source='gwas_catalog'
      ))

      # print pubmed_id, pvalue

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
    # it's an OR if there are no units
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