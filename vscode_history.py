#!/usr/bin/env python

# TODO reuse between get_files and get_files_by_regex

import json, os, re, sys
from collections import defaultdict

vscode_history_file = os.path.join(os.environ.get('HOME'), '.vscode_history')

def get_files(results = 20):
  '''
  Retrieve the most recently edited n files
  and match a filter if necessary
  '''
  file = open(vscode_history_file, 'r') 
  count = 0
  latest = defaultdict(int)

  for line in reversed(list(file)):
    # read as json
    cur_json = json.loads(line.rstrip('\n'))

    # group by file
    cur_filename = cur_json['filename']
    if cur_filename not in latest:
      count = count + 1

    latest[cur_filename] = latest[cur_filename] + 1
    if count % results == 0:
      break
  
  file.close()
  return latest

def get_files_by_regex(filter_string, results=50):
  '''
    Retrieve the most recently edited that match the regex
  '''
  print(f"Trying to match edited files that look like \"{filter_string}\"")
  file = open(vscode_history_file, 'r') 
  count = 0
  latest = defaultdict(int)

  pattern = re.compile(filter_string)

  for line in reversed(list(file)):
    # read as json
    cur_json = json.loads(line.rstrip('\n'))

    # group by file
    cur_filename = cur_json['filename']
    #print(cur_filename)

    if cur_filename not in latest and re.search(pattern, cur_filename):
      count = count + 1
      latest[cur_filename] = latest[cur_filename] + 1
      
    if count % results == 0:
      break
  
  file.close()
  return latest

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    if sys.argv[1].isnumeric():
      results = int(sys.argv[1])
      latest = get_files(results)
    else:
      filter_string = sys.argv[1]
      if len(sys.argv) == 3:
        latest = get_files_by_regex(filter_string, int(sys.argv[2]))
      else:
        latest = get_files_by_regex(filter_string)
  else:
    latest = get_files()

  for (key, value) in sorted(latest.items(), key=lambda k_v: k_v, reverse=False):
    print(f"{value} {key}")