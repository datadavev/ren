'''

'''

# List of character, character_replacement
REPLACE_CHARS = [
  [' ','-'],
  ["'",''],
  ['"',''],

]

def suggestFilename(original):
  suggested = original
  for change in REPLACE_CHARS:
    suggested = suggested.replace(change[0], change[1])
  return suggested

