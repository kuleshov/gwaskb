import os
import argparse
import re
import itertools

from bs4 import BeautifulSoup
from extractor.util import pvalue_to_float

# ----------------------------------------------------------------------------

def make_parser():
  parser = argparse.ArgumentParser()

  parser.add_argument('--dir')
  parser.add_argument('--map')
  parser.add_argument('--out')
  
  return parser

# ----------------------------------------------------------------------------

pval_rgx1 = re.compile(u'[1-9]\d?[\xb7\.]?\d*[\s\u2009]*[\xd7\xb7\*][\s\u2009]*10[\s\u2009]*[-\u2212\u2013\u2012][\s\u2009]*\d+')
pval_rgx2 = re.compile(u'[1-9]\d?[\xb7\.]?\d*[\s\u2009]*[eE][\s\u2009]*[-\u2212\u2013\u2012][\s\u2009]*\d+')
pval_rgx3 = re.compile(u'0\.0000+\d+')

rsid_rgx1 = re.compile(r'rs\d+(/[ATCG]{1,2})*$')

# ----------------------------------------------------------------------------

def matches_pval(txt):
  if pval_rgx1.match(txt) or pval_rgx2.match(txt) or pval_rgx3.match(txt):
    return True
  else:
    return False

def matches_rsid(txt):
  return True if rsid_rgx1.match(txt) else False

def parse_supp(dir, map, out):
  # load pmid/filename map
  name_map = {}
  with open(map) as f:
    for line in f:
      pmid, fname = line.strip().split('\t')
      fname = '.'.join(fname.split('.')[:-1]).lower() # remove extension
      name_map[fname] = pmid

  # clear output file
  with open(out, 'w') as fout: fout.write('')

  # parse supplementary material
  for fname in os.listdir(dir):
    fpath = os.path.join(dir, fname)
    
    if not os.path.isfile(fpath): continue
    if not fname.endswith('.html'): continue
    
    print 'Parsing file: %s' % fname

    with open(fpath) as f:
      ftext = f.read()
      soup = BeautifulSoup(ftext, 'lxml')

      fname = '.'.join(fname.split('.')[:-1]).lower() # remove extension
      pmid = name_map[fname]

      tables = soup.findAll('table')
      tfound = False
      for ti, table in enumerate(tables):
        tfound = True
        rows = table.findAll('tr')
        for ri, row in enumerate(rows):
          cells = row.findAll('td')
          pvals = [ ( ci, pvalue_to_float(c.text.strip()) ) 
                    for ci, c in enumerate(cells)
                    if matches_pval(c.text.strip()) ]
          rsids = [ ( ci, c.text.strip() ) for ci, c in enumerate(cells)
                    if matches_rsid(c.text.strip()) ]
          # for [(pval_idx, pval), (rsid_idx, rsid)] in itertools.product(pvals, rsids):
          #   print pmid, ti, ri, pval_idx, rsid_idx, pval, rsid

          with open(out, 'a') as fout: 
            for [(pval_idx, pval), (rsid_idx, rsid)] in itertools.product(pvals, rsids):
              fout.write('%s\t%s\t%d\t%d\t%d\t%f\n' % (pmid, rsid, ti, ri, rsid_idx, pval))


    # if tfound == True: exit()
  


def main():
  parser = make_parser()
  args = parser.parse_args()
  parse_supp(args.dir, args.map, args.out)

if __name__ == '__main__':
  main()