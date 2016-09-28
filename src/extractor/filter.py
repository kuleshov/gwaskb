import re
from bs4 import BeautifulSoup

from snorkel.parser import TableParser

# ----------------------------------------------------------------------------

class TableInspector(TableParser):
  def __init__(self, tok_whitespace=False):
    super(TableInspector, self).__init__(tok_whitespace)

  def inspect(self, document, text):
    results = []
    for table in self.parse_html(document, text):
      results.append(self.inspect_table(table))
    return results

  def inspect_table(self, table):
      soup = BeautifulSoup(table.text, 'lxml')
      position = 0

      # this will hold various observations we make about the table
      result = {
        'pval_header' : False,
        'phen_header' : False,
        'num_rsids' : 0, # num rows with rsids
        'num_rels' : 0, # rsid/regex pvalue relations
      }

      for row_num, row in enumerate(soup.find_all('tr')):
          col_num = 0
          row_has_rsid = False
          row_has_pval = False
          for html_cell in row.children:
              if html_cell.name in ['th','td']:
                  txt = unicode(html_cell.get_text(" ", strip=True))
                  if row_num == 0:
                    if _is_phen_title(txt): result['phen_header'] = True
                    if _is_pval_title(txt): result['pval_header'] = True

                  if _is_pval(txt): row_has_pval = True
                  if _is_rsid(txt): row_has_rsid = True
                  
          if row_has_rsid:
            result['num_rsids'] += 1
          if row_has_rsid and row_has_pval:
            result['num_rels'] += 1
                  
      return result

# ----------------------------------------------------------------------------
# helpers

rsid_rgx = r'rs\d+(/[^s]+)?'
pval_rgxs = [ u'[1-9]\d?[\xb7\.]?\d*\s*[\xd7\*]\s*10\s*[-\u2212\u2013]\s*\d+',
              u'[1-9]\d?[\xb7\.]?\d*\s*[eE][-\u2212\u2013]\d+',  
              u'0\.0000+\d+' ]
phen_title_rgxs = [ 'trait', 'outcome', 'phenotype' ]
pval_title_rgx = r'p\s?.?\s?val'

def _is_pval(txt):
  return True if any(re.search(pval_rgx, txt) for pval_rgx in pval_rgxs) else False

def _is_rsid(txt):
  return True if re.search(rsid_rgx, txt) else False

def _is_phen_title(txt):
  return True if any(re.search(phen_rgx, txt, re.IGNORECASE) for phen_rgx in phen_title_rgxs) else False

def _is_pval_title(txt):
  return True if re.search(pval_title_rgx, txt, re.IGNORECASE) and len(txt) < 20 else False