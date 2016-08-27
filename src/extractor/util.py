import re
import string
from nltk.stem import PorterStemmer

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
  pmids = set( [ (ngram.context.document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

  # only keep exponents
  gold = { (doc_id, floor(log10(pval))) for doc_id, pval in gold if pval > 0 }
  pmids = { (doc_id, floor(log10(pval))) for doc_id, pval in pmids if pval > 0 }

  strange = [p for p in pmids - gold]
  strange_pmids = set ([p[0] for p in strange])
  pval_dict = { doc_id : [] for doc_id, pval in strange }
  for doc_id, pval in strange:
      pval_dict[doc_id].append(pval)

  return [ ngram for ngram in candidates if ngram.context.document.name in strange_pmids
           and floor(log10(pvalue_to_float(ngram.get_attrib_span('words')))) in pval_dict[ngram.context.document.name]]

def gold_phen_stats(candidates, gold_set, phen2id):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  gold_dict = { doc_id : set() for doc_id, phen_id in gold }
  for doc_id, phen_id in gold:
    gold_dict[doc_id].add(phen_id)

  correct_candidates = set()
  for span in candidates:
    phen_name = span.get_span()
    phen_id = phen2id.get(change_name(phen_name), None)
    if phen_id in gold_dict[span.context.document.name]:
      correct_candidates.add( (span.context.document.name, phen_id) )

  # compute stats
  nc    = len(candidates)
  ng    = len(gold)
  both  = len(correct_candidates)
  print "Statistics over EFO phenotypes:"
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_phen_recall(candidates, gold_set, phen2id):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  gold_dict = { doc_id : set() for doc_id, phen_id in gold }
  for doc_id, phen_id in gold:
    gold_dict[doc_id].add(phen_id)

  correct_candidates = set()
  for span in candidates:
    phen_name = span.get_span()
    phen_id = phen2id.get(change_name(phen_name), None)
    if phen_id in gold_dict[span.context.document.name]:
      correct_candidates.add( (span.context.document.name, phen_id) )

  return gold - correct_candidates

def gold_agg_phen_stats(candidates, gold_set, phen2id):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  gold_dict = { doc_id : set() for doc_id, phen_id in gold }
  for doc_id, phen_id in gold:
    gold_dict[doc_id].add(phen_id)

  correct_candidates = set()
  for span in candidates:
    phen_name = span.get_span()
    phen_ids = phen2id.get(change_name(phen_name), None)
    if phen_ids:
      for phen_id in phen_ids & gold_dict[span.context.document.name]:
        correct_candidates.add( (span.context.document.name, phen_id) )

  # compute stats
  nc    = len(candidates)
  ng    = len(gold)
  both  = len(correct_candidates)
  print "Statistics over EFO phenotypes:"
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_agg_phen_recall(candidates, gold_set, phen2id):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  gold_dict = { doc_id : set() for doc_id, phen_id in gold }
  for doc_id, phen_id in gold:
    gold_dict[doc_id].add(phen_id)

  correct_candidates = set()
  for span in candidates:
    phen_name = span.get_span()
    phen_ids = phen2id.get(change_name(phen_name), None)
    if phen_ids:
      for phen_id in phen_ids & gold_dict[span.context.document.name]:
        correct_candidates.add( (span.context.document.name, phen_id) )

  return gold - correct_candidates

def gold_rspval_stats(candidates, gold_set):
  candidate_set = set([
    ( change_name(spanpair.span0.get_span()), get_exponent(pvalue_to_float(spanpair.span1.get_span())) )
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

def change_name(phen_name):
  DEL_LIST = ['measurement', 'levels', 'age', 'at', 'infection', 'major', 'test']
  stemmer = PorterStemmer()
  punctuation = set(string.punctuation)

  # reorder words with commas
  if ',' in phen_name:
    phen_words = phen_name.split(',')
    if len(phen_words) == 2:
      phen_name = ' '.join([phen_words[1], phen_words[0]])

  # remove punctuation
  phen_name = ''.join(ch for ch in phen_name if ch not in punctuation)

  phen_name = phen_name.lower()
  phen_words = phen_name.split()
  phen_name = ' '.join([stemmer.stem(word) for word in phen_words 
                        if word not in DEL_LIST])

  return phen_name
