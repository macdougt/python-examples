#!/usr/bin/env python

# TODO reuse between get_files and get_files_by_regex

import json, os, re, sys
from collections import defaultdict

vscode_history_file = os.path.join(os.environ.get('HOME'), '.vscode_history')

# Known type extensions
known_types = {
  'python':'.*py$',
  'py':'.*py$',
  'perl':'.*pl$',
  'pl':'.*pl$',
  'js':'.*js$',
  'javascript':'.*js$',
  'markdown':'.*md$',
  'md':'.*md$',
  'html':'.*html$',
}

class VsHistory():

  def __init__(self) -> None:
    self.latest = defaultdict(int)

  # Display known types and associations
  def types(self):
    import pprint
    pprint.pprint(known_types)

  def _get_files(self, results: int = 20):
    '''
    Retrieve the most recently edited n files
    and match a filter if necessary
    '''
    with open(vscode_history_file, 'r') as file:
      count = 0

      for line in reversed(list(file)):
        # read as json
        cur_json = json.loads(line.rstrip('\n'))

        # group by file
        cur_filename = cur_json['filename']
        if cur_filename not in self.latest:
          count += 1

        self.latest[cur_filename] = self.latest[cur_filename] + 1
        if count % results == 0:
          break
    return [k for k in self.latest.keys()]

  def _get_files_by_regex(self, filter_string, results=20):
    '''
    Retrieve the most recently edited that match the regex
    '''
    #print(f"Trying to match edited files (up to {results}) that look like \"{filter_string}\"")
    with open(vscode_history_file, 'r') as file:
      result_count = 1
      line_count = 0
      pattern = re.compile(filter_string)

      for line in reversed(list(file)):
        # read as json
        cur_json = json.loads(line.rstrip('\n'))
        line_count += 1

        # group by file
        cur_filename = cur_json['filename']

        if cur_filename not in self.latest and re.search(pattern, cur_filename):
          result_count += 1
          self.latest[cur_filename] = self.latest[cur_filename] + 1

        if result_count % (results + 1) == 0:
          break
      #print(f"Parsed {line_count} records")
    return [k for k in self.latest.keys()]

  def get_files(self, filter_pattern=None, type=None, results=20):
    '''
    Retrieve files that match specifications
    e.g.

    # Retrieve 20 results no filter
    vh get_files --results 20 

    # Retrieve 20 results match .*py$
    vh get_files --filter_pattern ".*py$" --results 20

    '''
    if type:
      if type in known_types:
        pattern = known_types[type]
        print(f"Looking for last {results} results matching file with {pattern}")
        return self._get_files_by_regex(pattern, results)
      else:
        print(f"Do not recognize type {type}\nReturning all")
        return self._get_files(results)
    if filter_pattern:
      return self._get_files_by_regex(filter_pattern, results)
    else:
      return self._get_files(results)

def display(results):
  #for (key, value) in sorted(results.items(), key=lambda k_v: k_v, reverse=False):
  for result in sorted(results):
    print(result)


class TestVsHistory():

  def test_get_files(self):
    vh = VsHistory()
    test_get_files_results = vh._get_files()
    print(f" Number of results: {len(test_get_files_results)}")
    assert len(test_get_files_results) > 0

  def test_get_files_by_regex(self):
    vh = VsHistory()
    test_get_files_by_regex_results = vh._get_files_by_regex(".*py$")
    print(f" Number of results: {len(test_get_files_by_regex_results)}")
    assert len(test_get_files_by_regex_results) > 0

  def test_get_files_with_known_type(self):
    vh = VsHistory()
    test_get_files_with_known_type_results = vh.get_files(type="javascript")
    print(f" Number of results: {len(test_get_files_with_known_type_results)}")
    assert len(test_get_files_with_known_type_results) > 0
    assert test_get_files_with_known_type_results[0].endswith('js')

if __name__ == "__main__":

  # Before going full CLI mode, process no args and single int argument
  if len(sys.argv) == 1:
    display(VsHistory().get_files())
  elif len(sys.argv) == 2 and sys.argv[1].isnumeric():
    display(VsHistory().get_files(results=int(sys.argv[1])))
  else:
    import fire
    fire.Fire(VsHistory)