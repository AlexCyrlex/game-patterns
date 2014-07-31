import re
import os
from collections import OrderedDict
from time import localtime, strftime

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

def generate_game_list(all_games):
  with open('../generated/AllGames.md', 'w') as fo:
    fo.write('All Games\n=========\nThis file is auto-generated; do not edit\n')
    for game in all_games:
      fo.write('* %s %s\n'% (game['Name'], game['Play Links'][0]))
      fo.write('  * %s\n' % game['Info Links'][0])
      patterns = ', '.join(x['key'] for x in game['Patterns'][1] if not x['key'].startswith('_'))
      fo.write('  * Patterns: %s\n' % patterns) 

def _add_pattern(pat, pat_dict, names, plus_checked = False, key = None):
  if key is None:
    key = pat['key']
    if key[0] == '_':
      return False

  if not plus_checked:
    parts = key.split('+')
    if len(parts)>1:
      for part in parts:
        _add_pattern(pat,pat_dict,names,plus_checked = True, key = part.strip())
      return False 
  
  if key in names:
    return False

  if key not in pat_dict:
    subpat = []
    pat_dict[key] = subpat
  else:
    subpat = pat_dict[key]
  val = pat.get('value',None)
  if val:
    subpat.append({'key': val, 'items':[]})
  subpat.extend(pat['items'])


def extract_new_patterns(all_games):
  patterns = parse_md('../patterns.md')
  names = {x[0] for x in patterns}
  pat_dict = OrderedDict()
  for game in all_games:
    for pat in game['Patterns'][1]:
      _add_pattern(pat, pat_dict, names)

  with open('../_pattern.md','r') as tfile:
    template = tfile.read()
  with open('../patterns.md','a') as pfile:
    pfile.write('# auto-extracted on %s\n\n' % strftime("%Y-%m-%d %H:%M:%S", localtime()))
    for key, val in pat_dict.iteritems():
      result = template.replace('_Name_', key)
      result = result.replace('* _Subpatterns_\n',unparse_list(val)) 
      pfile.write(result + '\n')

def unparse_list(lst, indent = 0):
  result = ''
  for item in lst:
    result += ' '* (2*indent) + '* '+ item['key']
    if 'value' in item:
        result += ': ' + item['value']
    result += '\n'
    if item['items']:
      result += unparse_list(item['items'],indent+1)
  if not result:
    result = '* _Subpatterns_\n'
  return result

all_games = [convert_game(parse_md('../games/'+x)) for x in os.listdir('../games') if not x.startswith('_')]

# print all_games
generate_game_list(all_games)
extract_new_patterns(all_games)       
          
          
        
      