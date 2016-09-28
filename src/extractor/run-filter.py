#!/usr/bin/env python
import os
import argparse

from parser import UnicodeXMLTableDocParser
from filter import TableInspector

# ----------------------------------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument('--dir', help='dir with xml files')
parser.add_argument('--sel', help='selected filenames')

args = parser.parse_args()

# ----------------------------------------------------------------------------

xml_parser = UnicodeXMLTableDocParser(
    path=args.dir,
    doc='//article',
    text='.//table',
    id='.//article-id[@pub-id-type="pmid"]/text()',
    keep_xml_tree=True)

inspector = TableInspector()

def _passes(res):
  return True if res['num_rels'] > 3 \
              or (res['pval_header'] and res['num_rsids'] > 5) \
              or (res['phen_header'] and res['num_rsids'] > 5) \
         else False

with open(args.sel, 'w') as out:
  for i, (doc, text) in enumerate(xml_parser.parse()):
    if i % 100 == 0: print i
    results = inspector.inspect(doc, text)
    if any(_passes(res) for res in results):
      print doc.name
      out.write('%s\n' % doc.name)
