import argparse
import numpy as np
from collections import defaultdict

# ----------------------------------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument('-k', '--known', required=True)
parser.add_argument('-n', '--new', required=True)
parser.add_argument('-o', '--out', required=True)

args = parser.parse_args()

# ----------------------------------------------------------------------------

# load known snps
known_pos = {str(i) : defaultdict(dict) for i in range(1,23) + ['X']}
with open(args.known) as f:
  f.readline()
  for line in f:
    fields = line.strip().split('\t')
    if ';' in fields[11]: continue
    if not fields[11] or not fields[12]: continue
    try: 
      pos = int(fields[12])
    except ValueError:
      continue
    chr = fields[11]
    pmid, rsid = fields[1], fields[21]
    known_pos[chr][pmid][rsid] = pos

# load new snps
new_pos = {str(i) : defaultdict(dict) for i in range(1,23) + ['X']}
with open(args.new) as f:
  for line in f:
    fields = line.strip().split()
    pmid, rsid = fields[1], fields[0]
    chr, pos = fields[2], int(fields[3])
    new_pos[chr][pmid][rsid] = pos

# load closest old snp to each new snp
out = open(args.out, 'w')
for chr in new_pos:
  for pmid in new_pos[chr]:
    for rsid, pos in new_pos[chr][pmid].items():
      gwcat_snps = known_pos[chr][pmid].items()
      gwcat_snps = sorted(gwcat_snps, key=lambda x:np.abs(x[1]-pos))
      if gwcat_snps: old_rsid, old_pos = gwcat_snps[0]
      else: old_rsid, old_pos = None, 0
      out.write('%s\t%s\t%s\t%d\t%s\t%d\t%d\n' % (pmid, rsid, chr, pos, old_rsid, old_pos, np.abs(old_pos - pos)))
