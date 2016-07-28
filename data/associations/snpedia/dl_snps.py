import argparse
import requests
import time
from wikitools import wiki, category, page

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--folder', help='Target folder')
  args = parser.parse_args()
  crawl(args.folder)

def crawl(folder):
  n = 0
  site = wiki.Wiki("http://bots.snpedia.com/api.php")
  for result in query({'cmtitle':'Category:Is_a_snp'}):
    for item in result.values()[0]:
      snp = item['title']
      if not (snp.startswith('I') or snp.startswith('R')):
        continue

      targetfile = folder + '/' + snp + '.txt'
      if not os.path.isfile(targetfile):
        pagehandle = page.Page(site,snp)
        snp_page = pagehandle.getWikiText()
        with open(targetfile, 'w') as f:
          f.write(snp_page)

      print n, snp
      time.sleep(0.5)
      n += 1
      # if n>3:exit()

def query(request):
  request['action'] = 'query'
  request['format'] = 'json'
  request['list'] = 'categorymembers'
  request['cmlimit'] = '5000'
  lastContinue = {'continue': ''}
  while True:
    # Clone original request
    req = request.copy()
    # Modify it with the values returned in the 'continue' section of the last result.
    req.update(lastContinue)
    # Call API
    result = requests.get('http://bots.snpedia.com/api.php', params=req).json()
    if 'error' in result:
        raise Error(result['error'])
    if 'warnings' in result:
        print(result['warnings'])
    if 'query' in result:
        yield result['query']
    if 'continue' not in result:
        break
    lastContinue = result['continue']

if __name__ == '__main__':
  main()
