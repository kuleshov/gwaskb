import argparse
import string
import unicodedata

from sqlalchemy.sql import exists, and_, or_

from wikitools import wiki, category

from db import db_session
from db.schema import *

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--init', action='store_true', help='Init db')
  parser.add_argument('--phenotypes', action='store_true', help='Load phenotypes')
  parser.add_argument('--snps', action='store_true', help='Start crawl; load snps')

  args = parser.parse_args()

  if args.init:
    init_db()

  if args.phenotypes:
    phenotypes(db_session)

  if args.snps:
    crawl(db_session)

def phenotypes(db_session):
  site = wiki.Wiki("http://bots.snpedia.com/api.php")
  snps = category.Category(site, "Is_a_snp")
  snpedia = []
    
  n = 0     
  for article in snps.getAllMembersGen(namespaces=[0]):
    snpedia.append(article.title.lower())
    print article.title
    n += 1
    print n
    if n > 5: break

def test():
  from wikitools import wiki, category, page
  import mwparserfromhell
  site = wiki.Wiki("http://bots.snpedia.com/api.php")
  snp = "rs7412"
  pagehandle = page.Page(site,snp)
  snp_page = pagehandle.getWikiText()

  wikicode = mwparserfromhell.parse(snp_page)
  templates = wikicode.filter_templates(recursive=False)
  for t in templates:
    print t.name, t.params


if __name__ == '__main__':
  main()
  # test()