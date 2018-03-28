'''
Suggest a file name using some best practices.

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
