import lxml.etree as et

from snorkel.parser import XMLDocParser, Document

# ----------------------------------------------------------------------------

class UnicodeXMLDocParser(XMLDocParser):
  """Changes default Snorkel XMLDocParser.

  String are stored in unicode.

  It also concatenates fields with a space instead of a newline (otherwise it
  breaks p-value formatting). 
  """

  def parse_file(self, f, file_name):
    for i,doc in enumerate(et.parse(f).xpath(self.doc)):
      text = ' '.join(filter(lambda t : t is not None, doc.xpath(self.text)))
      ids = doc.xpath(self.id)
      id = ids[0] if len(ids) > 0 else None
      attribs = {'root':doc} if self.keep_xml_tree else {}
      yield Document(id=str(id), file=str(file_name), text=unicode(text), attribs=attribs)