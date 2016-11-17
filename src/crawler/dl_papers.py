import argparse
import string
import unicodedata
import os
import requests
import urllib
import time

from xml.etree import ElementTree

from sqlalchemy.sql import exists, and_, or_

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--init', action='store_true', help='Init db')
  parser.add_argument('--mark-open-access', help='Path to open access list')
  parser.add_argument('--download-oa', help='Path to target folder')
  parser.add_argument('--wait', help='Wait time in between server calls',
                                type=int, default=1)

  args = parser.parse_args()

  if args.init:
    init_db()

  if args.mark_open_access:
    mark_oa(args.mark_open_access)

  if args.download_oa:
    download_oa(args.download_oa, args.wait)

def mark_oa(open_access):
  # load oa paper set
  pubmed_to_pmc = dict()
  with open(open_access) as f:
    f.readline()
    for line in f:
      fields = line.strip().split('\t')
      if len(fields) < 5: continue
      if not fields[3] or not fields[2]: continue
      pmid = int(fields[3][5:])
      pmc = fields[2]
      pubmed_to_pmc[pmid] = pmc

  # download papers that are open-access
  papers = db_session.query(Paper).all()
  open_access_papers = list()
  for paper in papers:
    if paper.pubmed_id in pubmed_to_pmc:
      # open-access!
      open_access_papers.append(paper)
      paper.open_access = True

  db_session.commit()

  assocs = [assoc for paper in open_access_papers for assoc in paper.associations ]

  print 'open access papers:', len(open_access_papers)
  print 'open associaitons:', len(assocs)
  print 'all papers:', db_session.query(Paper).count()
  print 'all associaitons:', db_session.query(Association).count()

def download_oa(folder, wait=1):
  open_papers = db_session.query(Paper).filter(Paper.open_access==True).all()
  n_open_papers = db_session.query(Paper).filter(Paper.open_access==True).count()
  for i, paper in enumerate(open_papers):
    print '%d/%d' % (i, n_open_papers)
    if not paper.pmc_id:
      paper.pmc_id = _get_pmc_id(paper.pubmed_id)
    if not paper.abstract:
      paper.abstract = _get_abstract(paper.pubmed_id)
    if not paper.files:
      # download xml body
      filename = str(paper.pubmed_id) + '.xml'
      
      if _get_oa_body(paper.pubmed_id, paper.pmc_id, folder):
        file = File(paper=paper, format='xml', filename=filename)
        db_session.add(file)

      # download pdf and supplementary
      files = _get_oa_pdf(paper.pubmed_id, paper.pmc_id, folder)
      for filename in files:
        if filename.endswith('.pdf'): format = 'pdf'
        elif filename.endswith('.tgz'): format = 'tgz'
        else: continue
        file = File(paper=paper, format='html', filename=filename)
        db_session.add(file)

    time.sleep(wait)

    db_session.commit()

# ----------------------------------------------------------------------------
# helpers

def _get_oa_pdf(pubmed_id, pmc_id, outfolder):
  url = 'http://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=%s' % pmc_id
  pdf_target = outfolder + '/' + str(pubmed_id) + '.pdf'
  tgz_target = outfolder + '/' + str(pubmed_id) + '.tgz'
  response = requests.get(url)
  root = ElementTree.fromstring(response.content)
  links = root.iter('link')
  files_dl = list()
  for link in links:
    if link.get('format') == 'pdf':
      if not os.path.isfile(pdf_target):
        if _dl_file(link.get('href'), pdf_target):
          files_dl.append( str(pubmed_id) + '.pdf' )
      else:
        files_dl.append( str(pubmed_id) + '.pdf' )
    elif link.get('format') == 'tgz':
      if not os.path.isfile(tgz_target):
        if _dl_file(link.get('href'), tgz_target):
          files_dl.append( str(pubmed_id) + '.tgz' )
      else:
        files_dl.append( str(pubmed_id) + '.tgz' )

  return files_dl

def _get_oa_body(pubmed_id, pmc_id, outfolder):
  pmc_id_num = int(pmc_id[3:])
  url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=%d' \
    % pmc_id_num
  response = requests.get(url)
  if response.status_code == requests.codes.ok:
    xml_target = outfolder + '/' + str(pubmed_id) + '.xml'
    if not os.path.isfile(xml_target):
      with open(xml_target, 'w') as f:
        f.write(response.content)
    return True
  else:
    return False

def _get_abstract(pubmed_id):
  url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%d&retmode=xml&rettype=abstract' % pubmed_id
  response = requests.get(url)
  root = ElementTree.fromstring(response.content)
  abstracts = root.iter('AbstractText')
  abstract_texts = list()
  for abstract in abstracts:
    abstract_texts.append(abstract.text)
  if abstract_texts:
    return abstract_texts[0]
  else:
    return None

def _get_html(pubmed_id, pmc_id, outfolder):
  url = 'https://http://europepmc.org/articles/%s' % pmc_id
  response = requests.get(url)
  if response.status_code == requests.codes.ok:
    html_target = outfolder + '/' + str(pubmed_id) + '.html'
    with open(html_target, 'w') as f:
      f.write(response.content)
    return True
  else:
    return False
  
def _get_supplementary(pubmed_id, pmc_id, outfolder):
  url = 'http://www.ebi.ac.uk/europepmc/webservices/rest/%s/supplementaryFiles' \
    % pmc_id
  response = requests.get(url)  
  tgz_target = outfolder + '/' + str(pubmed_id) + '-supp.tgz'
  return _dl_file(url, tgz_target)

def _dl_file(url, target):
  opener = urllib.URLopener()
  try:
    opener.retrieve(url, target)
    return True
  except IOError:
    return False

def _get_pmc_id(pubmed_id):
  url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=%d&versions=no' % pubmed_id
  response = requests.get(url)
  root = ElementTree.fromstring(response.content)
  records = root.iter('record')
  record_pmcs = list()
  for record in records:
    record_pmcs.append(record.get('pmcid'))
  if record_pmcs:
    return record_pmcs[0]
  else:
    return None

# ----------------------------------------------------------------------------

if __name__ == '__main__':
  # _get_oa_pdf('1234', 'PMC13901', '.')
  # _get_oa_body(1234, 'PMC13901', '.')
  # _get_supplementary(1234, 'PMC13901', '.')
  # print _get_abstract(20729146)
  # print _get_pmc_id(14699080)
  main()


# - dl list of open-access papers
# - for each open-access paper, get abstract, body, supplementary materials, store them as files
# - count number of papers
# - for the remaining ones: download abstract
# - later: download full pdf
# - look at how to mask ip during crawl

# notes:
# gwas catalog:
# open access papers: 590
# open associaitons: 9792
# all papers: 2088
# all associaitons: 25226

# snpedia (80%?)
# open access papers: 4297
# open associaitons: 6355
# all papers: 25393
# all associaitons: 14476

# joint (loose)
# open access papers: 4345
# open associaitons: 16166
# all papers: 25750
# all associaitons: 39757

# merged when name is the same:
# open access papers: 4358
# open associaitons: 15131
# all papers: 25750
# all associaitons: 39757

# merge all associations with same snp and paper
# open access papers: 4358
# open associaitons: 14774
# all papers: 25750
# all associaitons: 39757
