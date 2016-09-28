import xml
import lxml.etree as et
from bs4 import BeautifulSoup
from itertools import chain
from collections import defaultdict

from snorkel.parser import XMLDocParser, TableParser
from snorkel.models import Corpus, Document, Sentence, Table, Cell, Phrase
from snorkel.utils import corenlp_cleaner, sort_X_on_Y, split_html_attrs

# ----------------------------------------------------------------------------

class UnicodeXMLDocParser(XMLDocParser):
  """Changes default Snorkel XMLDocParser.

  String are stored in unicode.

  It also concatenates fields with a space instead of a newline (otherwise it
  breaks p-value formatting). 
  """

  def __init__(self, path, doc='.//document', text='./text/text()', id='./id/text()',
                    keep_xml_tree=False):
    XMLDocParser.__init__(self, path, doc, text, id, keep_xml_tree)

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f).xpath(self.doc)):
      text = ' '.join(filter(lambda t : t is not None, doc.xpath(self.text)))
      ids = doc.xpath(self.id)
      id = ids[0] if len(ids) > 0 else None
      attribs = {'root':doc} if self.keep_xml_tree else {}
      yield Document(name=str(id), file=str(file_name), attribs=attribs), unicode(text)

class GWASXMLAbstractParser(XMLDocParser):
  """For parsing GWAS pubmed papers

  It uses the title and abstract. If there is no abstract it uses par 1 instead.
  String are stored in unicode.
  """

  def __init__(self, path, doc, title, abstract, par1, id, keep_xml_tree=False):
    text = title + ' | ' + abstract
    XMLDocParser.__init__(self, path, doc, text, id, keep_xml_tree)
    self.title = title
    self.abstract = abstract
    self.par1 = par1

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f).xpath(self.doc)):
      title_text    = ' '.join(filter(lambda t : t is not None, doc.xpath(self.title)))
      abstract_text = ' '.join(filter(lambda t : t is not None, doc.xpath(self.abstract)))
      par1_text     = ' '.join(filter(lambda t : t is not None, doc.xpath(self.par1)))

      if not title_text.endswith('.'): title_text = title_text + '.'

      ids = doc.xpath(self.id)
      id = ids[0] if len(ids) > 0 else None
      attribs = {'root':doc} if self.keep_xml_tree else {}
      if abstract_text:
        text = title_text + ' ' + abstract_text
      else:
        text = title_text + ' ' + par1_text
      yield Document(name=str(id), file=str(file_name), attribs=attribs), unicode(text)

class GWASXMLDocParser(XMLDocParser):
  """For parsing GWAS pubmed papers

  It uses the title and abstract. If there is no abstract it uses par 1 instead.
  String are stored in unicode.
  """

  def __init__(self, path, doc, title, abstract, n_par, id, keep_xml_tree=False):
    text = title + ' | ' + abstract
    XMLDocParser.__init__(self, path, doc, text, id, keep_xml_tree)
    self.title = title
    self.abstract = abstract
    self.n_par = n_par

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f).xpath(self.doc)):
      title_text    = ' '.join(filter(lambda t : t is not None, doc.xpath(self.title)))
      abstract_text = ' '.join(filter(lambda t : t is not None, doc.xpath(self.abstract)))
      pars = doc.xpath('.//body//p')[:self.n_par]
      par_text = ' '.join(filter(lambda t : t is not None, [_et2str(t) for t in pars]))

      if not title_text.endswith('.'): title_text = title_text + '.'
      if not abstract_text.endswith('.'): abstract_text = abstract_text + '.'

      ids = doc.xpath(self.id)
      id = ids[0] if len(ids) > 0 else None
      attribs = {'root':doc} if self.keep_xml_tree else {}
      text = title_text + ' ' + abstract_text + ' ' + par_text
      yield Document(name=str(id), file=str(file_name), attribs=attribs), unicode(text) 

def _et2str(t):
  return ''.join(t.xpath('.//text()'))

# ----------------------------------------------------------------------------
# for tables

class UnicodeXMLTableDocParser(XMLDocParser):
  """Changes default Snorkel XMLDocParser.

  String are stored in unicode.

  It also concatenates fields with a space instead of a newline (otherwise it
  breaks p-value formatting). 
  """

  def __init__(self, path, doc='.//document', text='./text/text()', id='./id/text()',
                    keep_xml_tree=False):
    super(UnicodeXMLTableDocParser, self).__init__(path, doc, text, id, keep_xml_tree)

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f).xpath(self.doc)):
      # print et.tostring(doc)[:100]
      # print f
      # print et.parse('../data/db/papers/19305408.xml').xpath('./*')[0].xpath('.//table')
      # print doc.xpath('.//table')
      text = '\n'.join([ et.tostring(elem) for elem in doc.xpath(self.text) if elem is not None])
      ids = doc.xpath(self.id)
      # print i, ids
      id = ids[0] if len(ids) > 0 else None
      attribs = {'root':doc} if self.keep_xml_tree else {}
      # print 'ok ok', text, self.text
      yield Document(name=str(id), file=str(file_name), attribs=attribs), unicode(text)

  def _can_read(self, fpath):
    return fpath.endswith('.xml') or fpath.endswith('.nxml')

class UnicodeTableParser(TableParser):
  def __init__(self, tok_whitespace=False):
    super(UnicodeTableParser, self).__init__(tok_whitespace)

  def parse_table(self, table):
      soup = BeautifulSoup(table.text, 'lxml')
      position = 0
      for row_num, row in enumerate(soup.find_all('tr')):
          ancestors = ([(row.name, row.attrs.items())]
              + [(ancestor.name, ancestor.attrs.items())
              for ancestor in row.parents if ancestor is not None][:-2])
          (tags, attrs) = zip(*ancestors)
          html_anc_tags = tags
          html_anc_attrs = split_html_attrs(chain.from_iterable(attrs))
          col_num = 0
          for html_cell in row.children:
              # TODO: include title, caption, footers, etc.
              if html_cell.name in ['th','td']:
                  parts = defaultdict(list)
                  parts['document_id'] = table.document_id
                  parts['table_id'] = table.id
                  parts['position'] = position
                  parts['document'] = table.document
                  parts['table'] = table

                  parts['text'] = unicode(html_cell.get_text(" ", strip=True))
                  parts['row_num'] = row_num
                  parts['col_num'] = col_num
                  parts['html_tag'] = html_cell.name
                  parts['html_attrs'] = split_html_attrs(html_cell.attrs.items())
                  parts['html_anc_tags'] = html_anc_tags
                  parts['html_anc_attrs'] = html_anc_attrs
                  cell = Cell(**parts)
                  html_cell['snorkel_id'] = cell.id   # add new attribute to the html
                  yield cell
                  position += 1
                  col_num += 1