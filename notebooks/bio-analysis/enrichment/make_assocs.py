#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

# ----------------------------------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument('-k', '--known', required=True)
parser.add_argument('-n', '--new', required=True)
parser.add_argument('-m', '--mat', required=True)
parser.add_argument('-f', '--filtered', required=True)

args = parser.parse_args()

# ----------------------------------------------------------------------------

def parse_assocs(fname):
  pmid2rsid = dict()
  with open(fname) as f:
    for line in f:
      fields = line.strip().split()
      pmid, rsid = fields[:2]
      if pmid not in pmid2rsid:
        pmid2rsid[pmid] = []
      pmid2rsid.append(rsid)

known_a = parse_assocs(args.known)
new_a = parse_assocs(args.new)

# load matrix of p_values
known_rsids = sorted(set(known_a.values())):
r_scores = dict()
for rsid in sorted(set(new_a.values())):
  try:
    with open('link.%s.txt' % rsid) as f:
      for line in f:
        fields = line.strip().split()
        other_rsid = fields[5]
        r = float(fields[6])
        if other_rsid in known_rsids:
          if rsid not in r_scores:
            r_scores[rsid] = dict()
          r_scores[rsid][other_rsid] = r

  except Exception:
    print 'Exception for:', rsid

filtered_mat = open(args.mat, 'w')
filtered_a = open(args.filtered, 'w')

with open(args.new) as f:
  for line in f:
    fields = line.strip().split()
    pmid, rsid = fields[:2]
    r_list = [r_scores[rsid].get(known_rsid, 0.) for known_rsid in known_a[pmid]]
    for known_rsid, r in zip(known_a[pmids], r_list):
      filtered_mat.write('%s\t%s\t%s\t%f\n' % (pmid, rsid, known_rsid, r)
    # for known_rsid in known_a[pmids]:
    #   r = r_scores[rsid].get(known_rsid, 0.)
    #   filtered_mat.write('%s\t%s\t%s\t%f\n' % (pmid, rsid, known_rsid, r)
    r_max =max(r_list)
    filtered_a.write('\t'.join(fields) + '\t%f\n' % r_max)
