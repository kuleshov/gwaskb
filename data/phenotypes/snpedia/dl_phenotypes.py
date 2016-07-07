import string
import unicodedata
import argparse
from wikitools import wiki, category, page

# ----------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--diseases', help='Target disease file')
  parser.add_argument('--drugs', help='Target drug file')
  args = parser.parse_args()
  
  if args.diseases:
    get_diseases(args.diseases)
  
  if args.drugs:
    get_drugs(args.drugs)

def get_diseases(fname):
  site = wiki.Wiki("http://bots.snpedia.com/api.php")
  diseases = category.Category(site, "Is_a_medical_condition")
  n = 0     
  
  with open(fname, 'w') as f:
    for article in diseases.getAllMembersGen(namespaces=[0]):
      disease = _normalize_str(article.title.strip())
      f.write(disease + '\n')
      n += 1

  print 'diseases extracted:', n

def get_drugs(fname):
  site = wiki.Wiki("http://bots.snpedia.com/api.php")
  drugs = category.Category(site, "Is_a_medicine")
  n = 0     
  
  with open(fname, 'w') as f:
    for article in drugs.getAllMembersGen(namespaces=[0]):
      drug = _normalize_str(article.title.strip())
      f.write(drug + '\n')
      n += 1

  print 'drugs extracted:', n

def _normalize_str(s):
  return unicodedata.normalize('NFKD', s).encode('ascii','ignore')  

if __name__ == '__main__':
  main()