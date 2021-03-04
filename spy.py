#!/usr/bin/env python
import sys

# Gather all the files matching a pattern
import jsonlines, os, re
from collections import defaultdict
from rich.console import Console
from rich.table import Table


def find_pattern(pattern, filename, lines_around=2):
  '''
  Return all rows matching re.pattern
  '''
  # Create the result rows  
  rows = []

  with open(filename) as file:
    content = file.readlines()

  for i, line in enumerate(content):
    for match in re.finditer(pattern, line):
      for j in range(max(0, i-lines_around), min(i+lines_around,len(content))):
        if j == i:
          rows.append(f"{j+1}: {content[j]}")
        else:
          rows.append(content[j])
      rows.append("\n")
      #print(f"{file}: Found on line {i+1} {match.group()}")
      #print(line)
  return rows

def find(pattern_string, file):
  '''
  Return all rows matching pattern_string
  '''
  pattern = re.compile(pattern_string)
  return find_pattern(pattern, file)

if __name__ == "__main__":

  if len(sys.argv) < 2:
    # tag: debug input
    from bullet import colors, Input, VerticalPrompt
    questions = [
      Input(key="file_pattern", prompt="File pattern? ",
        default = ".*py$",
        word_color = colors.foreground["yellow"]
      ),
      Input(key="inner_pattern", prompt="Inner pattern? ",
        default = "bullet",
        word_color = colors.foreground["yellow"]
      ),
    ]
    prompt =  VerticalPrompt(questions)
    resulting_data = prompt.launch()
    file_pattern = resulting_data['file_pattern']
    inner_pattern = resulting_data['inner_pattern']
  elif len(sys.argv) < 3:
    # Assume python
    file_pattern = r'.*py$'
    inner_pattern = re.compile(sys.argv[1])
  else:  
    file_pattern = re.compile(sys.argv[1])
    inner_pattern = re.compile(sys.argv[2])

  vscode_history_file = os.path.join(os.environ.get('HOME'), '.vscode_history')
  unique_files = defaultdict(lambda: 0)

  with jsonlines.open(vscode_history_file) as reader:
      for obj in reader:
        #print(obj)
        # filter the filenames
        cur_filename = obj['filename']
        if re.search(file_pattern, cur_filename) and os.path.isfile(cur_filename):
          unique_files[cur_filename] = unique_files[cur_filename]+1

  table_rows = []

  # Search for a pattern inside the files
  for file in unique_files:
    cur_rows = find(inner_pattern, file)
    if cur_rows:
      cur_content = ''.join(row for row in cur_rows)
      table_rows.append((file, cur_content))
  
  if table_rows:
    # Build table
    console = Console()

    table = Table(show_header=True, header_style="bold blue", show_lines=True)
    table.add_column("Content", width=120)
    table.add_column("Line")

    for row in table_rows:
      table.add_row(
        row[1], f"vscode://file{row[0]}"
      )
    console.print(table)
    