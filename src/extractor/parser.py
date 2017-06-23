import os
import re
import xml
import lxml.etree as et
from bs4 import BeautifulSoup
from itertools import chain
from collections import defaultdict

from snorkel.parser import XMLMultiDocParser, OmniParser
from snorkel.models import Corpus, Document, Sentence, Table, Cell, Phrase
from snorkel.utils import corenlp_cleaner, sort_X_on_Y, split_html_attrs

# ----------------------------------------------------------------------------

class UnicodeXMLDocParser(XMLMultiDocParser):
  """Changes default Snorkel XMLDocParser.

  String are stored in unicode.

  It also concatenates fields with a space instead of a newline (otherwise it
  breaks p-value formatting). 
  """

  def __init__(self, path, doc='.//document', text='./text/text()', id='./id/text()',
                    keep_xml_tree=False):
    XMLMultiDocParser.__init__(self, path, doc, text, id, keep_xml_tree)

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f).xpath(self.doc)):
      text = ' '.join(filter(lambda t : t is not None, doc.xpath(self.text)))
      ids = doc.xpath(self.id)
      id = ids[0] if len(ids) > 0 else None
      attribs = {'root':doc} if self.keep_xml_tree else {}
      yield Document(name=str(id), file=str(file_name), attribs=attribs), unicode(text)

class SuppXMLDocParser(XMLMultiDocParser):
  """Changes default Snorkel XMLDocParser.

  Used for parsing supplementary material converted by LibreOffice.
  Only looks at tables.
  """

  def __init__(self, paths, map_path, doc='.//document', text='./text/text()', id='./id/text()',
                    keep_xml_tree=False):
    XMLMultiDocParser.__init__(self, paths[0], doc, text, id, keep_xml_tree)
    self.n=0
    self.paths = paths

    # load map
    self.map = {}
    with open(map_path) as f:
      for line in f:
        pmid, fname = line.strip().split('\t')
        fname = '.'.join(fname.split('.')[:-1]).lower() # remove extension
        # print fname, pmid
        self.map[fname] = pmid
        # if pmid not in self.map: self.map[pmid] = []
        # self.map[pmid].append(fname)

  def _get_files(self):
    fpaths = [os.path.join(path, f) for path in self.paths for f in os.listdir(path)]
    if len(fpaths) > 0:
        return fpaths
    else:
        raise IOError("No files found in provided directories: %s" % 
                      ', '.join(self.paths))

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f, et.HTMLParser()).xpath(self.doc)):
      ids = doc.xpath(self.id)
      # name = re.sub(r'\..*$', '', os.path.basename(f))
      name = os.path.basename(f)
      name = '.'.join(name.split('.')[:-1]).lower() # remove extension
      text = ' '.join([et.tostring(e) for e in filter(lambda t : t is not None, doc.xpath(self.text))])

      pmid = self.map[name]
      doc_id = '%s-%s' % (pmid, name)

      meta = {'file_name': str(file_name), 'pmid': pmid}
      if self.keep_xml_tree:
          meta['root'] = et.tostring(doc)
      stable_id = self.get_stable_id(doc_id)
      self.n += 1
      yield Document(name=doc_id, stable_id=stable_id, meta=meta), unicode(text)

  def _can_read(self, fpath):
    return fpath.endswith('.html')

class GWASXMLAbstractParser(XMLMultiDocParser):
  """For parsing GWAS pubmed papers

  It uses the title and abstract. If there is no abstract it uses par 1 instead.
  String are stored in unicode.
  """

  def __init__(self, path, doc, title, abstract, par1, id, keep_xml_tree=False):
    text = title + ' | ' + abstract
    XMLMultiDocParser.__init__(self, path, doc, text, id, keep_xml_tree)
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
      doc_id = ids[0] if len(ids) > 0 else None
      if abstract_text:
        text = title_text + ' ' + abstract_text
      else:
        text = title_text + ' ' + par1_text
      
      meta = {'file_name': str(file_name)}
      if self.keep_xml_tree:
          meta['root'] = et.tostring(doc)
      stable_id = self.get_stable_id(doc_id)
      yield Document(name=doc_id, stable_id=stable_id, meta=meta), unicode(text)

class GWASXMLDocParser(XMLMultiDocParser):
  """For parsing GWAS pubmed papers

  It uses the title and abstract. If there is no abstract it uses par 1 instead.
  String are stored in unicode.
  """

  def __init__(self, path, doc, title, abstract, n_par, id, keep_xml_tree=False):
    text = title + ' | ' + abstract
    XMLMultiDocParser.__init__(self, path, doc, text, id, keep_xml_tree)
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

      text = title_text + abstract_text + par_text

      ids = doc.xpath(self.id)
      doc_id = ids[0] if len(ids) > 0 else None
      doc_id += '-doc'  
      meta = {'file_name': str(file_name)}
      if self.keep_xml_tree:
          meta['root'] = et.tostring(doc)
      stable_id = self.get_stable_id(doc_id)
      yield Document(name=doc_id, stable_id=stable_id, meta=meta), unicode(text)

def _et2str(t):
  return ''.join(t.xpath('.//text()'))

# ----------------------------------------------------------------------------
# for tables

class UnicodeXMLTableDocParser(XMLMultiDocParser):
  """Changes default Snorkel XMLMultiDocParser.

  String are stored in unicode.

  It also concatenates fields with a space instead of a newline (otherwise it
  breaks p-value formatting). 
  """

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f).xpath(self.doc)):
      text = '\n'.join([ et.tostring(elem) for elem in doc.xpath(self.text) if elem is not None])
      ids = doc.xpath(self.id)
      doc_id = ids[0] if len(ids) > 0 else None
      meta = {'file_name': str(file_name)}
      if self.keep_xml_tree:
          meta['root'] = et.tostring(doc)
      stable_id = self.get_stable_id(doc_id)
      yield Document(name=doc_id, stable_id=stable_id, meta=meta), text

  def _can_read(self, fpath):
    return fpath.endswith('.xml') or fpath.endswith('.nxml')
