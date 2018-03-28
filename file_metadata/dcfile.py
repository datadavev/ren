'''
Get/Set XMP metadata in a file that supports it
'''

import sys
import logging
from pytz import timezone
import dateparser
from libxmp import XMPFiles, consts

DATE_FORMAT = "%Y-%m-%dT"
DEFAULT_TIMEZONE = "EST"


def textToDateTime(txt, default_tz='UTC'):
  logger = logging.getLogger('main')
  d = dateparser.parse(txt, settings={'RETURN_AS_TIMEZONE_AWARE': True})
  if d is None:
    logger.error("Unable to convert '%s' to a date time.", txt)
    return d
  if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
    logger.warning('No timezone information specified, assuming ' + DEFAULT_TIMEZONE)
    return d.replace(tzinfo=timezone(DEFAULT_TIMEZONE))
  return d


class DCFile(object):
  def __init__(self, fpath, lang='x-default'):
    self._xmp = None
    self._xmpfile = None
    self.fpath = fpath
    self.lang = lang
    self.allow_identifier_change = False
    self.array_properties = {'prop_array_is_ordered': True, 'prop_value_is_array': True}
    self.terms = ['dccoverage',
                  'dccreator',
                  'dcdescription',
                  'dcidentifier',
                  'dcpublisher',
                  'dcrelation',
                  'dcsource',
                  'dcsubject',
                  'dctitle',
                  'dctype',
                  ]
    self.open()

  def open(self):
    self._xmpfile = XMPFiles(file_path=self.fpath, open_forupdate=True)
    self._xmp = self._xmpfile.get_xmp()

  def close(self):
    if self._xmpfile is not None:
      if self._xmp is not None:
        self._xmpfile.put_xmp(self._xmp)
      self._xmpfile.close_file()
    self._xmp = None
    self._xmpfile = None

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.close()

  # -----------------------------------
  # Simple strings

  @property
  def dcidentifier(self):
    return self._xmp.get_property(consts.XMP_NS_DC, 'identifier')

  @dcidentifier.setter
  def dcidentifier(self, v):
    existing_id = self.dcidentifier
    if self.allow_identifier_change or (existing_id is None or existing_id == ''):
      res = self._xmp.set_property(consts.XMP_NS_DC, 'identifier', v)
    raise ValueError("Identifier already set and is immutable.")

  @property
  def dcsource(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'source'):
      return None
    return self._xmp.get_property(consts.XMP_NS_DC, 'source')

  @dcsource.setter
  def dcsource(self, v):
    res = self._xmp.set_property(consts.XMP_NS_DC, 'source', v)

  @dcsource.deleter
  def dcsource(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'source'):
      return
    self._xmp.delete_property(consts.XMP_NS_DC, 'source')

  @property
  def dccoverage(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'coverage'):
      return None
    return self._xmp.get_property(consts.XMP_NS_DC, 'coverage')

  @dccoverage.setter
  def dccoverage(self, v):
    res = self._xmp.set_property(consts.XMP_NS_DC, 'coverage', v)

  @dccoverage.deleter
  def dccoverage(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'coverage'):
      return
    self._xmp.delete_property(consts.XMP_NS_DC, 'coverage')

  # -----------------------------------
  # Localized strings

  @property
  def dctitle(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'title'):
      return None
    v = self._xmp.get_localized_text(consts.XMP_NS_DC, 'title', 'Alt', self.lang)
    return v

  @dctitle.setter
  def dctitle(self, v):
    res = self._xmp.set_localized_text(consts.XMP_NS_DC, 'title', 'Alt', self.lang, v)

  @dctitle.deleter
  def dctitle(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'title'):
      return
    self._xmp.delete_property(consts.XMP_NS_DC, 'title')

  @property
  def dcdescription(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'description'):
      return None
    v = self._xmp.get_localized_text(consts.XMP_NS_DC, 'description', 'Alt', self.lang)
    return v

  @dcdescription.setter
  def dcdescription(self, v):
    res = self._xmp.set_localized_text(consts.XMP_NS_DC, 'description', 'Alt', self.lang, v)

  @dcdescription.deleter
  def dcdescription(self):
    if not self._xmp.does_property_exist(consts.XMP_NS_DC, 'description'):
      return
    self._xmp.delete_property(consts.XMP_NS_DC, 'description')

  # -----------------------------------
  # multi-values

  @property
  def dccreator(self):
    '''
    :return: list of creator values
    '''
    res = []
    n = self._xmp.count_array_items(consts.XMP_NS_DC, 'creator')
    for i in xrange(0, n):
      res.append(self._xmp.get_array_item(consts.XMP_NS_DC, 'creator', i + 1))
    return res

  @dccreator.setter
  def dccreator(self, v):
    '''
    Set or append creator

    v may be single item or list.

    Appended to existing entries if any.
    '''
    if not isinstance(v, list):
      v = [v, ]
    for sv in v:
      self._xmp.append_array_item(consts.XMP_NS_DC, 'creator', sv, self.array_properties)

  @dccreator.deleter
  def dccreator(self):
    self._xmp.delete_property(consts.XMP_NS_DC, 'creator')

  @property
  def dcsubject(self):
    '''
    :return: list of creator values
    '''
    res = []
    n = self._xmp.count_array_items(consts.XMP_NS_DC, 'subject')
    for i in xrange(0, n):
      res.append(self._xmp.get_array_item(consts.XMP_NS_DC, 'subject', i + 1))
    return res

  @dcsubject.setter
  def dcsubject(self, v):
    '''
    Set or append subject

    v may be single item or list.

    Appended to existing entries if any.
    '''
    if not isinstance(v, list):
      v = [v, ]
    for sv in v:
      self._xmp.append_array_item(consts.XMP_NS_DC, 'subject', sv, self.array_properties)

  @dcsubject.deleter
  def dcsubject(self):
    self._xmp.delete_property(consts.XMP_NS_DC, 'subject')

  @property
  def dctype(self):
    '''
    :return: list of creator values
    '''
    res = []
    n = self._xmp.count_array_items(consts.XMP_NS_DC, 'type')
    for i in xrange(0, n):
      res.append(self._xmp.get_array_item(consts.XMP_NS_DC, 'type', i + 1))
    return res

  @dctype.setter
  def dctype(self, v):
    '''
    Set or append subject

    v may be single item or list.

    Appended to existing entries if any.
    '''
    if not isinstance(v, list):
      v = [v, ]
    for sv in v:
      self._xmp.append_array_item(consts.XMP_NS_DC, 'type', sv, self.array_properties)

  @dctype.deleter
  def dctype(self):
    self._xmp.delete_property(consts.XMP_NS_DC, 'type')

  @property
  def dcrelation(self):
    '''
    :return: list of creator values
    '''
    res = []
    n = self._xmp.count_array_items(consts.XMP_NS_DC, 'relation')
    for i in xrange(0, n):
      res.append(self._xmp.get_array_item(consts.XMP_NS_DC, 'relation', i + 1))
    return res

  @dcrelation.setter
  def dcrelation(self, v):
    '''
    Set or append subject

    v may be single item or list.

    Appended to existing entries if any.
    '''
    if not isinstance(v, list):
      v = [v, ]
    for sv in v:
      self._xmp.append_array_item(consts.XMP_NS_DC, 'relation', sv, self.array_properties)

  @dcrelation.deleter
  def dcrelation(self):
    self._xmp.delete_property(consts.XMP_NS_DC, 'relation')

  @property
  def dcpublisher(self):
    '''
    :return: list of creator values
    '''
    res = []
    n = self._xmp.count_array_items(consts.XMP_NS_DC, 'publisher')
    for i in xrange(0, n):
      res.append(self._xmp.get_array_item(consts.XMP_NS_DC, 'publisher', i + 1))
    return res

  @dcpublisher.setter
  def dcpublisher(self, v):
    '''
    Set or append subject

    v may be single item or list.

    Appended to existing entries if any.
    '''
    if not isinstance(v, list):
      v = [v, ]
    for sv in v:
      self._xmp.append_array_item(consts.XMP_NS_DC, 'publisher', sv, self.array_properties)

  @dcpublisher.deleter
  def dcpublisher(self):
    self._xmp.delete_property(consts.XMP_NS_DC, 'publisher')


if __name__ == '__main__':
  fn = sys.argv[1]
  with DCFile(fn) as dc:
    #for term in dc.terms:
    #  print(term + ': ' + str(getattr(dc, term)))
    for i in dc._xmp:
      print("{}:{}:{}".format(i[0],i[1],i[2]))
