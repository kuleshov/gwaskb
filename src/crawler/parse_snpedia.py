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
  parser.add_argument('--snps', help='Folder with snpedia snps in <snp_id>.txt format')

  args = parser.parse_args()

  if args.init:
    init_db()

  if args.snps:
    crawl(args.snps, db_session)

def crawl(folder, db_session):
  n = 0
  for file in os.listdir(folder):
    if not file.endswith('.txt'): continue
    with open(fodler + '/' + file) as f:
      snp_name = file[:-4]
      wikicode = mwparserfromhell.parse(f.read())
      templates = wikicode.filter_templates(recursive=False)

      # site = wiki.Wiki("http://bots.snpedia.com/api.php")
      # snp_name = "rs7412"
      # pagehandle = page.Page(site,snp_name)
      # snp_page = pagehandle.getWikiText()

      # wikicode = mwparserfromhell.parse(snp_page)
      # templates = wikicode.filter_templates(recursive=True)

      # get SNP
      snp = db_session.query(SNP).filter(SNP.rs_id==snp_name).first()
      if not snp:
        snp = SNP(rs_id=snp_name)

      for t in templates:
        tname = t.name.strip()

        if tname == 'Rsnum':
          # store SNP params
          chrom = _parse_entry(t, 'Chromosome', out_type=int)
          pos = _parse_entry(t, 'Position', out_type=int)
          gene = _parse_entry(t, 'Gene')
          ref = _parse_entry(t, 'Assembly')

          if not snp.chrom: snp.chrom = chrom
          if not snp.position: snp.position = pos
          if not snp.gene: snp.gene = gene
          if not snp.ref: snp.ref = ref

        elif tname == 'PMID Auto GWAS':
          # store GWAS box
          trait = _normalize_str(_parse_entry(t, 'Trait'))
          pmid = _parse_entry(t, 'PMID', out_type=int)
          title = _parse_entry(t, 'Title')
          allele = _parse_entry(t, 'RiskAllele')
          pvalue = _parse_entry(t, 'Pval', out_type=float)
          or_entry = _parse_entry(t, 'OR', out_type=float)
          or_text = _parse_entry(t, 'ORtxt')
          openaccess = _parse_entry(t, 'OA', out_type=bool)

          if pmid is None: continue
          
          if not openaccess: openaccess = False
          if or_text: 
            beta, oddsratio = or_entry, None
          else:
            beta, oddsratio = None, or_entry

          # create/lookup paper
          paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
          if not paper:
            paper = Paper(pubmed_id=pmid, title=title, snpedia_open=openaccess)
            db_session.add(paper)

          # create/lookup phenotype
          phenotype = db_session.query(Phenotype).filter(and_(
                        Phenotype.name==trait,
                        Phenotype.source=='snpedia',
                      )).first() # max 1 phenotype from snpedia
          if not phenotype:
            phenotype = Phenotype(name=trait, source='snpedia')
            db_session.add(phenotype)

          # create association
          db_session.add(Association(
            snp=snp,
            phenotype=phenotype,
            paper=paper,
            pvalue=pvalue,
            oddsratio=oddsratio,
            beta=beta,
            allele=allele,
            source='snpedia'
          ))

        elif tname in ('PMID Auto', 'PMID'):
          # save mentions in papers
          pmid = _parse_entry(t, 'PMID')
          title = _parse_entry(t, 'Title')
          openaccess = _parse_entry(t, 'OA', out_type=bool)

          if pmid is None: continue
          
          if not openaccess: openaccess = False
          automatic = True if tname == 'PMID Auto' else False

          # create/lookup paper
          paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
          if not paper:
            paper = Paper(pubmed_id=pmid, title=title, snpedia_open=openaccess)
            db_session.add(paper)

          db_session.add(SnpediaEvidence(snp=snp, paper=paper, 
                                         snpedia_open=openaccess, 
                                         automatic=automatic))
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