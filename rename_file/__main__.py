'''
Interact with GPG Encrypted password files in YAML format.

This script provides readonly access to a structured password
file in YAML syntax.

The YAML file has a structure like:

# Comments start with a "#"
DESCRIPTION: |
  This is a human readable description of this file.

RECIPIENTS:
  - list of
  - recipients of
  - the encrypted file

some_key:
  user: name of account (required)
  password: the password or phrase (required)
  name: human readable name of entry (optional)
  note: |
    optional note. The pipe char indicates that
    line breaks will be preserved, but the
    preceding space on each line will not.
  other: Other properties may be added as needed.

'''

import sys
import os
import argparse
import logging
from . import *


#==============================================
def main():
  parser = argparse.ArgumentParser(description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-l', '--log_level',
                      action='count',
                      default=0,
                      help='Set logging level, multiples for more detailed.')
  parser.add_argument('-s','--suggest',
                      action='store_true',
                      help="Suggest only")
  parser.add_argument('source',
                      nargs='?',
                      default=None,
                      help='File to rename')
  args = parser.parse_args()
  # Setup logging verbosity
  levels = [logging.WARNING, logging.INFO, logging.DEBUG]
  level = levels[min(len(levels) - 1, args.log_level)]
  logging.basicConfig(level=level,
                      format="%(asctime)s %(levelname)s %(message)s")
  #override logging in gnupg module
  glogger = logging.getLogger('rename_file')
  glogger.setLevel(logging.ERROR)

  if not os.path.exists(args.source):
    logging.warning("Path %s not found.", args.source)
    args.suggest = True

  suggested_name = suggestFilename(args.source)
  print(suggested_name)
  if args.suggest:
    sys.exit(0)
  os.rename(args.source, suggested_name)

if __name__ == "__main__":
  main()
