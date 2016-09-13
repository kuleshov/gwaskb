import argparse
import string
import unicodedata
import os
import requests
import re
import xml.etree.ElementTree as ET
from lxml import etree
from io import StringIO

from sqlalchemy.sql import exists, and_, or_

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--init', action='store_true', help='Init db')
  parser.add_argument('--ids', help='List of paper ids')
  parser.add_argument('--min-neg-log-pval', default=5, type=int)

  args = parser.parse_args()

  if args.init:
    init_db()

  if args.ids:
    crawl(args.ids, args.min_neg_log_pval)

# ----------------------------------------------------------------------------

def crawl(pubmed_id_f, cutoff):
  # collect papers to parse
  pubmed_ids = list()
  with open(pubmed_id_f) as f:
    pubmed_ids = [int(line.strip()) for line in f]

  # download GWC data for each paper
  for pmid in pubmed_ids:
    # get study identifier
    gwcid = pmid2gwcid(pmid)

    # get list of results
    results = gwcid2results(gwcid)

    # create/load paper
    paper = db_session.query(Paper).filter(Paper.pubmed_id==pmid).first()
    if not paper:
      paper = Paper(pubmed_id=pmid)
      db_session.add(paper)
      db_session.commit()

    phenotypes = dict()
    snps = dict()
    for result in results:
      rsid, resultset_id, resultset_link, pvalue, neglog_pvalue = result

      if neglog_pvalue < cutoff: continue

      # if phenotype is not known, retrieve it
      if resultset_id not in phenotypes:
        phenotype_name = res2phen(resultset_id, resultset_link)
        phenotype = Phenotype(name=phenotype_name, source='gwas_central')
        phenotypes[resultset_id] = phenotype
        db_session.add(phenotype)
        db_session.commit()
      else:
        phenotype = phenotypes[resultset_id]

      # create snp
      if rsid not in snps:
        snp = db_session.query(SNP).filter(SNP.rs_id==rsid).first()
        if not snp:
          snp = SNP(rs_id=rsid)
          db_session.add(snp)
          db_session.commit()
      else:
        snp = snps[rsid]

      # create association
      db_session.add(Association(
        snp=snp,
        phenotype=phenotype,
        paper=paper,
        pvalue=pvalue,
        source='gwas_central'
      ))

      print 'Extracted association:', paper.pubmed_id, phenotype.name, snp.rs_id, pvalue

  db_session.commit()

# ----------------------------------------------------------------------------

def pmid2gwcid(pmid):
  payload = {'format': 'json', 'q' : '%d' % pmid}
  r = requests.get('http://www.gwascentral.org/studies', params=payload)
  json = r.json()

  # there should be only one study matching this pmid
  if not len(json) == 1:
    print 'WARNING: >1 studies match pmid', pmid

  return json[0]['identifier']

def gwcid2results(gwcid):
  payload = {'format': 'json'}
  url = 'http://www.gwascentral.org/study/%s/results' % gwcid
  r = requests.get(url, params=payload)

  json = r.json()

  return [ ( e['accession'], e['resultset'], e['related_data'][0]['link'], 
             float(e['pvalue']), float(e['neglog_pvalue']) ) for e in json ]

def res2phen(resultset_id, resultset_link):
  payload = {'format': 'html'}
  url = 'http://www.gwascentral.org/' + resultset_link
  r = requests.get(url, params=payload)
  html = r.text

  root = etree.HTML(html)
  rows = root.xpath(".//table[@class='summary']/tr")

  phen_name = None
  for row in rows:
    # print row.text
    children = [child for child in row]
    if len(children) != 2: continue
    if children[0].text != 'Phenotype': continue
    if phen_name is not None: exit('!!!')
    phen_name = children[1].xpath('.//text()')[0]

  # remove parantheses
  phen_name = re.sub('\(.+\)', '', phen_name)
  phen_name = phen_name.strip()

  return phen_name

if __name__ == '__main__':
  main()
