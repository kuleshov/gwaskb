import re

from math import floor, log10

# ----------------------------------------------------------------------------
# statistics

def gold_rsid_stats(candidates, gold_set):
  """Computes gold stats for rsids

  Our gold annotations are for documents, not words, so we need
  our own functions to compute stats.
  """

  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (ngram.doc_id, ngram.get_attrib_span('words')) for ngram in candidates] )
  nc    = len(pmids)
  ng    = len(gold)
  both  = len(gold.intersection(pmids))
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_rsid_precision(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (ngram.doc_id, ngram.get_attrib_span('words')) for ngram in candidates] )
  strange = [p for p in pmids - gold]
  strange_pmids = set ([p[0] for p in strange])
  return [ngram for ngram in candidates if ngram.doc_id in strange_pmids]

def gold_pval_stats(candidates, gold_set):
  """Computes gold stats for pvalues

  We only ask for the exponent to be correct.
  """

  # store collected and gold sets
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (ngram.doc_id, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

  # only keep exponents
  gold = { (doc_id, floor(log10(pval))) for doc_id, pval in gold if pval > 0 }
  pmids = { (doc_id, floor(log10(pval))) for doc_id, pval in pmids if pval > 0 }

  # compute stats
  nc    = len(pmids)
  ng    = len(gold)
  both  = len(gold.intersection(pmids))
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_pval_precision(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (ngram.doc_id, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

  # only keep exponents
  gold = { (doc_id, floor(log10(pval))) for doc_id, pval in gold if pval > 0 }
  pmids = { (doc_id, floor(log10(pval))) for doc_id, pval in pmids if pval > 0 }

  strange = [p for p in pmids - gold]
  strange_pmids = set ([p[0] for p in strange])
  pval_dict = { doc_id : [] for doc_id, pval in strange }
  for doc_id, pval in strange:
      pval_dict[doc_id].append(pval)

  return [ ngram for ngram in candidates if ngram.doc_id in strange_pmids
           and floor(log10(pvalue_to_float(ngram.get_attrib_span('words')))) in pval_dict[ngram.doc_id]]

# ----------------------------------------------------------------------------
# other helpers

def pvalue_to_float(pstr):
  # extract groups via regex
  rgx = u'(\d+\.?\d*)\s*\xd7\s*10\s*\u2212\s*(\d+)'
  result = re.search(rgx, pstr)

  # convert the result to a float
  if result:
    groups = result.groups()
    if len(groups) == 2:
      multiplier = float(groups[0])
      exponent = float(groups[1])    
      return multiplier * 10 ** -exponent
  
  return None