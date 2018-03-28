'''

'''
import os
import platform
import logging
import datetime
import datefinder
import textract

# List of character, character_replacement
REPLACE_CHARS = [
  ["'", ''],
  ['"', ''],
  [',', '']
]


#Date format for suggested file name
DATE_FORMAT_NAME = "%Y%m%d_"
NAME_DATE            = 1  # Use date in filename if available
METADATA_CREATE_DATE = 2  # Fallback to create date in metadata
CONTENT_DATE         = 3  # Use first date found in the file content
FILE_CREATE_DATE     = 4  # Use the file creation date if nothing else works

FILENAME_DATE_PRIORITY = (
  NAME_DATE,
  METADATA_CREATE_DATE,
  CONTENT_DATE,
  FILE_CREATE_DATE,
)

def dateFromFileName(fname, ignore_partial=True):
  '''
  List of date, (start,end) index found in file name.
  Args:
    fname: File name to examine
    ignore_partial: True if partial dates are to be ignored

  Returns:
    list of (date, (start index, end index))
  '''
  #This date is used to identify partial matches
  basedate = datetime.datetime(3000,1,1)
  matches = datefinder.find_dates(fname, index=True, base_date=basedate)
  result = []
  for match in matches:
    if match[0].year != basedate.year:
      result.append(match)
  return result


def dateFileCreated(fname):
  '''
  Try to get the date that a file was created, falling back to when it was
  last modified if that isn't possible.
  See http://stackoverflow.com/a/39501288/1709587 for explanation.
  '''
  ctime = None
  if platform.system() == 'Windows':
    ctime = os.path.getctime(fname)
  else:
    stat = os.stat(fname)
    try:
      ctime = stat.st_birthtime
    except AttributeError:
      # We're probably on Linux. No easy way to get creation dates here,
      # so we'll settle for when its content was last modified.
      ctime = stat.st_mtime
  return datetime.datetime.fromtimestamp(ctime)


def datesFromMetadata(fname):
  return ()


def datesFromContent(fname):
  file_text = textract.process(fname).decode("utf-8")
  #This date is used to identify partial matches
  basedate = datetime.datetime(3000,1,1)
  dates = datefinder.find_dates(file_text, strict=True, source=True, base_date=basedate)
  res = []
  max = 3
  i = 0
  for date in dates:
    res.append((date[0], date[1]))
    i += 1
    if i > max:
      break
  return res


def getDateFromFile(fname):
  '''
  Figure out a date for the provided file.

  1. Check file name for date metadata
  2. look at xmp metadata
    a. dublin core
    b. adobe
    c.
  3. Suggest file creation date
  Args:
    fname:

  Returns:
    (date string, possibly altered filename)
  '''
  parts = os.path.splitext(os.path.basename(fname))
  logging.debug("Parts = %s", str(parts))
  new_name = parts[0]
  date_str = ''
  file_exists = os.path.exists(fname)
  for date_check in FILENAME_DATE_PRIORITY:
    if date_check == NAME_DATE:
      dates_found = dateFromFileName(new_name)
      if len(dates_found) > 0:
        the_date = dates_found[0]
        date_str = the_date[0].strftime(DATE_FORMAT_NAME)
        logging.debug("Found date in filename: %s", date_str)
        name_start = new_name[:the_date[1][0]]
        new_name = name_start + new_name[the_date[1][1]:]
        new_name = os.path.join(os.path.dirname(fname),  new_name + parts[1])
        return date_str, new_name
    elif date_check == METADATA_CREATE_DATE:
      if file_exists:
        dates_found = datesFromMetadata(fname)
        if len(dates_found) > 0:
          the_date = dates_found[0]
          date_str = the_date[0].strftime(DATE_FORMAT_NAME)
          logging.debug("Found date in metadata: %s", date_str)
          return date_str, fname
    elif date_check == CONTENT_DATE:
      if file_exists:
        dates_found = datesFromContent(fname)
        if len(dates_found) > 0:
          the_date = dates_found[0]
          date_str = the_date[0].strftime(DATE_FORMAT_NAME)
          logging.debug("Found date in content: %s from %s", date_str, the_date[1])
          return date_str, fname
    elif date_check == FILE_CREATE_DATE:
      if file_exists:
        the_date = dateFileCreated(fname)
        date_str = the_date.strftime(DATE_FORMAT_NAME)
        logging.debug("Using create date of: %s", date_str)
        return date_str, fname
  return date_str, new_name


def suggestFilename(original, use_date=None):
  suggested = original
  date_str = ''
  if use_date is not None:
    date_str = use_date.strftime(DATE_FORMAT_NAME)
  else:
    date_str, suggested = getDateFromFile(original)

  # Replace spaces with underscores if dashes are present, otherwise dashes
  if suggested.find("-") > 0:
    suggested = suggested.replace(' ', '_')
  else:
    suggested = suggested.replace(' ', '-')

  # Replace characters that are annoying
  for change in REPLACE_CHARS:
    suggested = suggested.replace(change[0], change[1])
  result = "{}{}".format(date_str, suggested)
  return result

