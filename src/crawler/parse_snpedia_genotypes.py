import argparse
import string
import unicodedata
import os

from sqlalchemy.sql import exists, and_, or_

from wikitools import wiki, category, page
import mwparserfromhell

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--init', action='store_true', help='Init db')
  parser.add_argument('--genotypes', help='Folder with snpedia snps in <snp_id>.txt format')

  args = parser.parse_args()

  if args.init:
    init_db()

  if args.genotypes:
    crawl(args.genotypes, db_session)

def crawl(folder, db_session):
  # n = 0
  # for file in os.listdir(folder):
  #   if not file.endswith('.txt'): continue
  #   with open(fodler + '/' + file) as f:
  #     snp_name = file[:-4]
  #     wikicode = mwparserfromhell.parse(f.read())
  #     templates = wikicode.filter_templates(recursive=False)

  site = wiki.Wiki("http://bots.snpedia.com/api.php")
  snp_name = "Rs7412(C;C)"
  pagehandle = page.Page(site,snp_name)
  snp_page = pagehandle.getWikiText()

  wikicode = mwparserfromhell.parse(snp_page)
  templates = wikicode.filter_templates(recursive=True)

  # get SNP

  for t in templates:
    tname = t.name.strip()

    if tname == 'Genotype':
      rs_id = _parse_entry(t, 'rsid')
      allele1 = _parse_entry(t, 'allele1')
      allele2 = _parse_entry(t, 'allele2')
      magnitude = _parse_entry(t, 'magnitude', out_type=float)
      repute = _parse_entry(t, 'repute')
      summary = _normalize_str(_parse_entry(t, 'summary'))
      genotype = allele1 + allele2

      # get snp
      snp = db_session.query(SNP).filter(SNP.rs_id==rs_id).first()
      if not snp:
        snp = SNP(rs_id=rs_id)

      # create association
      db_session.add(Association(
        snp=snp,
        genotype=genotype,
        magnitude=magnitude,
        repute=repute,
        description=summary,
        source='snpedia'
      ))
      
  db_session.commit()

# ----------------------------------------------------------------------------
# helpers

def _parse_entry(t, name, out_type=None):
  try:
    s = t.get(name).value.strip()
  except ValueError:
    return None

  if s:
    if out_type: s = out_type(s)
    return s
  else:
    return None

def _normalize_str(s):
  s = s.decode('utf-8')
  return unicodedata.normalize('NFKD', s).encode('ascii','ignore')

if __name__ == '__main__':
  main()