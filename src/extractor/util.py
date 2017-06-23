import re
import string

from math import floor, log10

# ----------------------------------------------------------------------------
# statistics

def _context(candidate):
  return candidate.get_attributes()[0].parent

def gold_rsid_stats(candidates, gold_set):
  """Computes gold stats for rsids

  Our gold annotations are for documents, not words, so we need
  our own functions to compute stats.
  """

  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (_context(ngram).document.name, ngram.get_attrib_span('words')) for ngram in candidates] )
  nc    = len(pmids)
  ng    = len(gold)
  both  = len(gold.intersection(pmids))
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_rsid_recall(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (_context(ngram).document.name, ngram.get_attrib_span('words')) for ngram in candidates] )
  missing = [p for p in gold - pmids]
  missing_pmids = set ([p[0] for p in missing])
  return gold - pmids

def gold_rsid_precision(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (_context(ngram).document.name, ngram.get_attrib_span('words')) for ngram in candidates] )
  strange = [p for p in pmids - gold]
  return [ngram for ngram in candidates if (_context(ngram).document.name, ngram.get_span()) in strange]

def gold_pval_stats(candidates, gold_set):
  """Computes gold stats for pvalues

  We only ask for the exponent to be correct.
  """

  # store collected and gold sets
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (_context(ngram).document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

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
  rsids_found = { _context(ngram).document.name : set() for ngram in rsid_candidates }
  for ngram in rsid_candidates:
    rsids_found[_context(ngram).document.name].add(str(ngram.get_attrib_span('words')))
  gold = set([ (pmid, assoc.pvalue) for pmid in gold_set_dict for assoc in gold_set_dict[pmid] if pmid in rsids_found and str(assoc.snp.rs_id) in rsids_found[pmid] ])
  pmids = set( [ (_context(ngram).document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

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
  rsids_found = { _context(ngram).document.name : set() for ngram in rsid_candidates }
  for ngram in rsid_candidates:
    rsids_found[_context(ngram).document.name].add(str(ngram.get_attrib_span('words')))
  gold = set([ (pmid, assoc.pvalue) for pmid in gold_set_dict for assoc in gold_set_dict[pmid] if pmid in rsids_found and str(assoc.snp.rs_id) in rsids_found[pmid] ])
  pmids = set( [ (_context(ngram).document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

  # only keep exponents
  gold = { (doc_id, floor(log10(pval))) for doc_id, pval in gold if pval > 0 }
  pmids = { (doc_id, floor(log10(pval))) for doc_id, pval in pmids if pval > 0 }

  return gold - pmids

def gold_pval_precision(candidates, gold_set):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  pmids = set( [ (_context(ngram).document.name, pvalue_to_float(ngram.get_attrib_span('words'))) for ngram in candidates] )

  # only keep exponents
  gold = { (doc_id, floor(log10(pval))) for doc_id, pval in gold if pval > 0 }
  pmids = { (doc_id, floor(log10(pval))) for doc_id, pval in pmids if pval > 0 }

  strange = [p for p in pmids - gold]
  strange_pmids = set ([p[0] for p in strange])
  pval_dict = { doc_id : [] for doc_id, pval in strange }
  for doc_id, pval in strange:
      pval_dict[doc_id].append(pval)

  return [ ngram for ngram in candidates if _context(ngram).document.name in strange_pmids
           and floor(log10(pvalue_to_float(ngram.get_attrib_span('words')))) in pval_dict[_context(ngram).document.name]]

def gold_phen_stats(candidates, gold_set, phen2id):
  gold  = gold_set if isinstance(gold_set, set) else set(gold_set)
  gold_dict = { doc_id : set() for doc_id, phen_id in gold }
  for doc_id, phen_id in gold:
    gold_dict[doc_id].add(phen_id)

  correct_candidates = set()
  for span in candidates:
    phen_name = span.get_span()
    phen_id = phen2id.get(change_name(phen_name), None)
    if phen_id in gold_dict[_context(span).document.name]:
      correct_candidates.add( (_context(span).document.name, phen_id) )

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
    if phen_id in gold_dict[_context(span).document.name]:
      correct_candidates.add( (_context(span).document.name, phen_id) )

  return gold - correct_candidates

def gold_agg_phen_stats(candidates, gold_set, phen2id):
  # doc_id -> set of GWC ids found in doc
  gold_dict = { doc_id : set() for doc_id, phen_id in gold_set }
  for doc_id, phen_id in gold_set:
    gold_dict[doc_id].add(phen_id)

  # (doc_id, gwc_id) that are in gold and in candidates
  correct_candidates = set()
  for span in candidates:
    phen_name = span.get_span()
    phen_ids = phen2id.get(change_name(phen_name), None) # aggregate ids
    if phen_ids:
      for phen_id in phen_ids & gold_dict[_context(span).document.name]:
        correct_candidates.add( (_context(span).document.name, phen_id) )

  assert len(correct_candidates - gold_set) == 0 # ours is subset of gold_set

  # compute stats
  nc    = len(candidates)
  ng    = len(gold_set)
  both  = len(correct_candidates)
  print "Statistics over EFO phenotypes:"
  print "# of gold annotations\t= %s" % ng
  print "# of candidates\t\t= %s" % nc
  print "# of correct candidates\t= %s" % both
  print "Candidate recall\t= %0.3f" % (both / float(ng),)
  print "Candidate precision\t= %0.3f" % (both / float(nc),)

def gold_agg_phen_recall(candidates, gold_set, phen2id):
# doc_id -> set of GWC ids found in doc
  gold_dict = { doc_id : set() for doc_id, phen_id in gold_set }
  for doc_id, phen_id in gold_set:
    gold_dict[doc_id].add(phen_id)

  # (doc_id, gwc_id) that are in gold and in candidates
  correct_candidates = set()
  for span in candidates:
    phen_name = span.get_span()
    phen_ids = phen2id.get(change_name(phen_name), None) # aggregate ids
    if phen_ids:
      for phen_id in phen_ids & gold_dict[_context(span).document.name]:
        correct_candidates.add( (_context(span).document.name, phen_id) )

  assert len(correct_candidates - gold_set) == 0 # ours is subset of gold_set

  return gold_set - correct_candidates

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

def gold_rspval_precision(candidates, gold_set):
  signatures = [
    ( change_name(spanpair.span0.get_span()), get_exponent(pvalue_to_float(spanpair.span1.get_span())) )
    for spanpair in candidates
  ]

  gold_exp_set = set([ (rs_id, get_exponent(pval)) for rs_id, pval in gold_set ])
  missing_candidates = [candidate for candidate, signature in zip(candidates, signatures)
                        if signature not in gold_exp_set]
  
  return missing_candidates

# ----------------------------------------------------------------------------
# other helpers

def make_ngrams(L, n_max=10, n_min=3, delim=' '):
    for l in L:
        yield l
        tokens = l.strip().split(delim)
        for ngram in slice_into_ngrams(tokens, n_max=n_max, n_min=n_min, delim=delim):
            yield ngram

def slice_into_ngrams(tokens, n_max=3, n_min=1, delim='_'):
    N = len(tokens)
    for root in range(N):
        for n in range(max(0,n_min-1), min(n_max, N - root)):
            yield delim.join(tokens[root:root+n+1])

def pvalue_to_float(pstr, log=True):
  # extract groups via regex
  # rgx1 = u'([1-9]\d?[\.\xb7]?\d*)\s*[\xd7\*]\s*10\s*[-\u2212\u2013]\s*(\d+)'
  rgx1 = u'([1-9]\d?[\xb7\.]?\d*)[\s\u2009]*[\xd7\xb7\*][\s\u2009]*10[\s\u2009]*[-\u2212\u2013\u2012][\s\u2009]*(\d+)'
  result1 = re.search(rgx1, pstr)
  # rgx2 = u'([1-9]\d?[\xb7\.]?\d*)\s*[eE][-\u2212\u2013](\d+)'
  rgx2 = u'([1-9]\d?[\xb7\.]?\d*)[\s\u2009]*[eE][\s\u2009]*[-\u2212\u2013\u2012][\s\u2009]*(\d+)'
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
      if log:
        return -exponent + log10(multiplier)
      else:
        return multiplier * 10 ** -exponent
  elif result2:
    groups = result2.groups()
    if len(groups) == 2:
      mult_str = groups[0].replace(u'\xb7', '.')
      multiplier = float(mult_str)
      exponent = float(groups[1])    
      if log:
        return -exponent + log10(multiplier)
      else:
        return multiplier * 10 ** -exponent
  elif result3:
    groups = result2.groups()
    if len(groups) == 1:
      if log:
        return log10(float(groups[0]))
      else:
        return float(groups[0])

  try:
    pval = float(pstr)
    if log: pval = log10(pval)
  except Exception:
    print pstr
    return None

  return pval

def get_exponent(flt):
  if flt is not None:
    if flt == 0: return -10**6 #something really big
    return floor(log10(flt))
  else:
    return flt
  
  return None

def change_name(phen_name):
  import unidecode
  from nltk.stem import PorterStemmer

  DEL_LIST = ['measurement', 'levels', 'age at', 'response to', 'infection', 'major', 'test', 'size', 'disorder', 'symptom', 'trait', 'disease']
  stemmer = PorterStemmer()
  punctuation = set(string.punctuation)

  # reorder words with commas
  if ',' in phen_name:
    phen_words = phen_name.split(',')
    if len(phen_words) == 2:
      phen_name = ' '.join([phen_words[1], phen_words[0]])

  # reorder words in parantheses a b, (c d) -> c d a b
  phen_name = re.sub('(.+),? \((.+)\)$', '\g<2> \g<1>', phen_name)

  # replace dashes by spaces
  phen_name = phen_name.replace('-', ' ')

  # # remove punctuation #TODO: remove?
  # phen_name = ''.join(ch for ch in phen_name if ch not in punctuation)

  # remove other characters #TODO: remove?
  phen_name = re.sub(u"[\u2019']", '', phen_name)

  # fix unicode string
  phen_name = unidecode.unidecode(phen_name)

  # remove stopwords
  phen_name = phen_name.lower()
  for word in DEL_LIST:
    phen_name = re.sub(word, '', phen_name)

  # stem words
  phen_words = phen_name.split()
  phen_name = ' '.join([stemmer.stem(word) for word in phen_words 
                        if word not in DEL_LIST])

  return phen_name
