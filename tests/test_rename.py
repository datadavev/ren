import logging
import unittest
import rename_file

class TestFileRename(unittest.TestCase):

  def test_filenameDataeParse(self):
    test_names = (
      ('10 aug 1977 some file name.txt','19770810_some-file-name.txt'),
      ('Reply 10 10 18.vie version 1.docx','20181010_Reply.vie-version-1.docx'),
      ('Reply 10 10 18.vie version-1.docx','20181010_Reply.vie_version-1.docx')
    )
    for test in test_names:
      fres = rename_file.suggestFilename(test[0])
      self.assertEqual(fres, test[1])


  def test_fileCreateDate(self):
    pass


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  unittest.main()