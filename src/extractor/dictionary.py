

# ----------------------------------------------------------------------------
# dictionary for resolving acronyms

class Dictionary(object):
  def __init__(self):
    self.storage = dict()
    self.evidence = dict()

  def load(self, fname):
    with open(fname) as f:
      for line in f:
        doc_id, phen, acro = line.strip().split('\t')
        acro = acro.lower()
        phen = phen.lower()

        # add document
        if doc_id not in self.storage:
          self.storage[doc_id] = dict()
          self.evidence[doc_id] = dict()
        
        # add phenotype
        L = self.storage[doc_id].get(acro, set())
        L.add(phen)
        self.storage[doc_id][acro] = L

        # add evidence
        ev = self.evidence[doc_id].get((acro, phen), 0)
        ev += 1
        self.evidence[doc_id][(acro, phen)] = ev

  def find(self, doc_id, acronym):
    acronym = acronym.lower()
    if doc_id not in self.storage: return None
    L = list(self.storage[doc_id].get(acronym, []))
    
    if len(L) == 0: return None
    if len(L) == 1: return L[0]

    L = sorted(L, key=lambda x: self.evidence[doc_id][(acronym, x)], reverse=True)
    return L[0]


  def __len__(self):
    return sum(len(v) for v in self.storage.values())

# ----------------------------------------------------------------------------
# transform strings with dictionary

def unravel(doc_id, text, D):
  words = text.split()
  replace_word = lambda w : D.find(doc_id, w) if D.find(doc_id, w) else w
  new_words = ' '.join(replace_word(w) for w in words)

  return new_words
