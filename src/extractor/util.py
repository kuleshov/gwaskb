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
  pmids = set( [ (ngram.context.document.name, ngram.get_attrib_span('words')) for ngram in candidates] )
  nc    = len(pmids)
  ng    = len(gold)
  both  = len(gold.intersection(pmids))
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_rsid_recall(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (ngram.context.document.name, ngram.get_attrib_span('words')) for ngram in candidates] )
  missing = [p for p in gold - pmids]
  missing_pmids = set ([p[0] for p in missing])
  return gold - pmids

def gold_rsid_precision(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (ngram.context.document.name, ngram.get_attrib_span('words')) for ngram in candidates] )
  strange = [p for p in pmids - gold]
  return [ngram for ngram in candidates if (ngram.context.document.name, ngram.get_span()) in strange]

def gold_pval_stats(candidates, gold_set):
  """Computes gold stats for pvalues

  We only ask for the exponent to be correct.
  """

  # store collected and gold sets
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (ngram.context.document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

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

def gold_pval_stats_limited(candidates, gold_set_dict, rsid_candidates):
  """Computes gold stats for pvalues

  We only ask for the exponent to be correct.
  """

  # store collected and gold sets
  rsids_found = { ngram.context.document.name : set() for ngram in rsid_candidates }
  for ngram in rsid_candidates:
    rsids_found[ngram.context.document.name].add(str(ngram.get_attrib_span('words')))
  gold = set([ (pmid, assoc.pvalue) for pmid in gold_set_dict for assoc in gold_set_dict[pmid] if pmid in rsids_found and str(assoc.snp.rs_id) in rsids_found[pmid] ])
  pmids = set( [ (ngram.context.document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

  print list(sorted(gold))[:10]
  # only keep exponents
  gold = { (doc_id, floor(log10(pval))) for doc_id, pval in gold if pval > 0 }
  pmids = { (doc_id, floor(log10(pval))) for doc_id, pval in pmids if pval > 0 }

  print list(sorted(gold))[:10]
  print list(sorted(pmids))[:10]

  # compute stats
  nc    = len(pmids)
  ng    = len(gold)
  both  = len(gold.intersection(pmids))
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_pval_recall(candidates, gold_set_dict, rsid_candidates):
  """Computes gold stats for pvalues

  We only ask for the exponent to be correct.
  """

  # store collected and gold sets
  rsids_found = { ngram.context.document.name : set() for ngram in rsid_candidates }
  for ngram in rsid_candidates:
    rsids_found[ngram.context.document.name].add(str(ngram.get_attrib_span('words')))
  gold = set([ (pmid, assoc.pvalue) for pmid in gold_set_dict for assoc in gold_set_dict[pmid] if pmid in rsids_found and str(assoc.snp.rs_id) in rsids_found[pmid] ])
  pmids = set( [ (ngram.context.document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

  # only keep exponents
  gold = { (doc_id, floor(log10(pval))) for doc_id, pval in gold if pval > 0 }
  pmids = { (doc_id, floor(log10(pval))) for doc_id, pval in pmids if pval > 0 }

  return gold - pmids

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

def gold_phen_stats(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  gold_dict = { doc_id : set() for doc_id, phen in gold }
  for doc_id, phen in gold:
    gold_dict[doc_id].add(phen)

  n_both = 0
  n_tot = 0
  for ngram in candidates:
    phen = ngram.get_attrib_span('words')
    if phen in gold_dict[ngram.doc_id]:
      n_both += 1
    n_tot += 1

  # compute stats
  nc    = n_tot
  ng    = len(gold)
  both  = n_both
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_phen_recall(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  gold_dict = { doc_id : set() for doc_id, phen in gold }
  for doc_id, phen in gold:
    gold_dict[doc_id].add(phen)

  cand_dict = { ngram.doc_id : set() for ngram in candidates }
  for ngram in candidates: cand_dict[ngram.doc_id].add(ngram.get_attrib_span('words'))

  not_found = list()
  for doc_id, doc_candidates in cand_dict.items():
    doc_not_found = gold_dict[doc_id] - doc_candidates
    not_found.extend([(doc_id, word) for word in doc_not_found])

  return not_found

def gold_rspval_stats(candidates, gold_set):
  candidate_set = set([
    ( spanpair.span0.get_span().lower(), get_exponent(pvalue_to_float(spanpair.span1.get_span())) )
    for spanpair in candidates
  ])

  gold_exp_set = set([ (rs_id, get_exponent(pval)) for rs_id, pval in gold_set ])

  # compute stats
  nc    = len(candidate_set)
  ng    = len(gold_exp_set)
  both  = len(gold_exp_set.intersection(candidate_set))
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)


# ----------------------------------------------------------------------------
# other helpers

def pvalue_to_float(pstr):
  # extract groups via regex
  rgx1 = u'([1-9]\d?[\.\xb7]?\d*)\s*[\xd7\*]\s*10\s*[-\u2212\u2013]\s*(\d+)'
  result1 = re.search(rgx1, pstr)
  rgx2 = u'([1-9]\d?[\xb7\.]?\d*)\s*[eE][-\u2212\u2013](\d+)'
  result2 = re.search(rgx2, pstr)
  rgx3 = u'(0\.0000+\d+)'
  result3 = re.search(rgx2, pstr)

  # convert the result to a float
  if result1:
    groups = result1.groups()
    if len(groups) == 2:
      mult_str = groups[0].replace(u'\xb7', '.')
      multiplier = float(mult_str)
      exponent = float(groups[1])    
      return multiplier * 10 ** -exponent
  elif result2:
    groups = result2.groups()
    if len(groups) == 2:
      mult_str = groups[0].replace(u'\xb7', '.')
      multiplier = float(mult_str)
      exponent = float(groups[1])    
      return multiplier * 10 ** -exponent
  elif result3:
    groups = result2.groups()
    if len(groups) == 1:
      return float(groups[0])

def get_exponent(flt):
  if flt is not None:
    return floor(log10(flt))
  else:
    return flt
  
  return None