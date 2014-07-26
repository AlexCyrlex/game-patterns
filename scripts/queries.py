import re
import os

H1_LINE = re.compile('^=+$')
LIST_START = re.compile(r'^(\s*)\* (.*)$')

def _parse_line(text):
  pos = text.find(':')
  if pos == -1:
    return {'key':text,'items':[]}
  else:
    return {'key':text[:pos].rstrip(), 'value':text[pos+1:].lstrip(),'items':[]}

def _get_item(root, level):
  if level==0:
    return root
  else:
    e = root[-1]['items']
    return _get_item(e, level - 1) 

def parse_md(filename):
  with open(filename,'r') as fo:
    result = []
    waiting_header = True
    for line in fo:
      line = line.rstrip('\n')
      if waiting_header:
        if H1_LINE.match(line):
          # second line of header - switch to body mode
          waiting_header = False
        else:
          # first line of header - remember it
          entry = [line.strip(),'',[]]
      else:
        match = LIST_START.match(line)
        if match:
          # list item
          spaces, text = match.groups()
          level = len(spaces) / 2
          item = _parse_line(text)
          _get_item(entry[-1],level).append(item)
        elif line.strip() == '':
          # entry ended
          result.append(entry)
          waiting_header = True
        else:
          # description
          entry[1] = line
    return result      

def convert_game(md):
  """ Convert game data from generic MD list to more specific dict
  """
  result = {}
  [name, description, items] = md[0]
  result['Name'] = name
  if description:
    result['Description'] = description
  for item in items:
    result[item['key']] = item['value'], item['items']
  for item in md[1:]:
    [name, value, items] = item
    result[name] = value, items
  return result
  


all_games = [convert_game(parse_md('../games/'+x)) for x in os.listdir('../games') if not x.startswith('_')]

print all_games

            
          
          
        
      