import re
from snorkel.matchers import NgramMatcher, WORDS

from extractor.util import pvalue_to_float

class PvalMatcher(NgramMatcher):
  """Base regex class- does not specify specific semantics of *what* is being matched yet"""
  def init(self):
    self.ignore_case = self.opts.get('ignore_case', True)
    self.attrib      = self.opts.get('attrib', WORDS)
    self.sep         = self.opts.get('sep', " ")

    # Compile regex matcher
    rgx1 = u'[1-9]\d?[\xb7\.]?\d*\s*[\xd7\*]\s*10\s*[-\u2212\u2013]\s*\d+$'
    rgx2 = u'[1-9]\d?[\xb7\.]?\d*\s*[eE][-\u2212\u2013]\d+$'
    rgx3 = u'0\.0000+\d+$'

    self.r1 = re.compile(rgx1, flags=re.I if self.ignore_case else 0)
    self.r2 = re.compile(rgx2, flags=re.I if self.ignore_case else 0)
    self.r3 = re.compile(rgx3, flags=re.I if self.ignore_case else 0)

    self.n=0

  def _f(self, c):
    string = c.get_attrib_span(self.attrib, sep=self.sep)
    if self.r1.match(string) is not None \
    or self.r2.match(string) is not None \
    or self.r3.match(string) is not None:
      pval = pvalue_to_float(string)
      if 0 <= pval <= 1e-5:
        return True
    
    # otherwise  
    return False