
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
