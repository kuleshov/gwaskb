import argparse
import time
from wikitools import wiki, category, page

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--folder', help='Target folder')
  args = parser.parse_args()
  crawl(args.folder)

def crawl(folder):
  site = wiki.Wiki("http://bots.snpedia.com/api.php")
  snps = category.Category(site, "Is_a_snp")
  n = 0

  for article in snps.getAllMembersGen(namespaces=[0]):
    snp = article.title.lower()
    pagehandle = page.Page(site,snp)
    snp_page = pagehandle.getWikiText()
    with open(folder + '/' + snp + '.txt', 'w') as f:
      f.write(snp_page)

    print n, snp
    time.sleep(0.5)
    n += 1
    # if n>3:exit()

if __name__ == '__main__':
  main()
