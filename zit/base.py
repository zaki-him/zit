from . import data
import os
from datetime import date , datetime
from collections import namedtuple
import operator
import itertools

def is_ignored(path):
  return '.zit' in path.split('/')

def write_tree(directory = '.'):

  entries = [] # Collect (name, object_id, type) for all files and folders

  # Iterate through all entries in the current directory
  with os.scandir(directory) as it:
    for entry in it:
      full = f'{directory}/{entry.name}'

      #skip the .zit directory
      if is_ignored(full):
        continue

      if entry.is_file(follow_symlinks=False):
        # Files are stored as 'blob' objects
        type_ = 'blob'
        with open(full, 'rb') as f:
          object_id = data.hash_object(f.read())
      
      elif entry.is_dir(follow_symlinks=False):
        # Directories are stored as 'tree' objects
        type_ = 'tree'
        # Recursively process this directory and get its tree hash
        object_id = write_tree(full)

      # Append entry for BOTH files and directories
      # This builds the directory listing that will form the 'tree' object.
      entries.append((entry.name, object_id, type_))
  
  # Build the tree content:
  # Each line has format: "<type> <oid> <name>"
  tree = ''.join (f'{type_} {object_id} {name}\n'
                     for name, object_id, type_
                     in sorted (entries))
  
  # Hash the tree content and store it as a 'tree' object
  return data.hash_object (tree.encode (), 'tree')


def _iter_tree_entries(object_id):
  if not object_id:
    return
  tree = data.get_object(object_id, 'tree') # we get something like this: b'blob a3f1... file1.txt\nblob 7c2d... file2.txt\ntree b72e... src\n'
  for entry in tree.decode().splitlines(): # this will make it like this: ["blob a3f1... file1.txt", "blob 7c2d... file2.txt", "tree b72e... src"]
    type_, object_id, name = entry.split(' ', 2)

    # Yield this entry as a tuple (type, object_id, name).
    # Using 'yield' turns this function into a generator:
    # - It returns one entry at a time instead of building a full list.
    # - The function pauses here and resumes on the next iteration.
    yield type_, object_id, name

def get_tree(object_id, base_path=''):
  results = {}
  for type_, entry_object_id, name in _iter_tree_entries(object_id):
    assert '/' not in name # No slashes allowed in a single tree entry name
    assert name not in ('..', '.') # Disallow parent/current directory references

    path = base_path + name
    if type_ == 'blob':
      results[path] = entry_object_id
    elif type_ == 'tree':
      results.update(get_tree(entry_object_id, f'{path}/'))
    else:
      # If we encounter an unknown object type, stop execution
      assert False, f'Unknown tree entry {type_}'
  
  return results

def _empty_current_dir():
  for root, dirs, files in os.walk('.',topdown=True): # yields tuple (root, dirs, files)
    for filename in files:
      path = os.path.relpath(f'{root}/{filename}')
      if is_ignored(path) or not os.path.isfile(path): # safety check
        continue
      os.remove(path)
    for directory in dirs:
      path = os.path.relpath(f'{root}/{directory}')
      if is_ignored(path):
        continue
      try:
        os.rmdir(path)
      except(FileNotFoundError, OSError):
        pass

def read_tree(tree_oid):
  _empty_current_dir()
  for path, entry_object_id in get_tree(tree_oid, base_path='./').items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
      f.write(data.get_object(entry_object_id))


def commit(message):
  day = date.today()
  time = datetime.now()
  time_str = time.strftime("%H:%M:%S")

  commit = f'commit {write_tree()}'
  commit += '\n'

  HEAD = data.get_HEAD()

  if HEAD:
    commit += f'parent {HEAD}\n'

  commit += f'{time_str} {day}'
  commit += '\n'
  commit += f'{message}'

  object_id = data.hash_object(commit.encode(), 'commit')

  data.set_HEAD(object_id)

  return object_id

Commit = namedtuple('Commit', ['tree', 'parent', 'message'])

def get_commit(object_id):
  parent = None

  commit = data.get_object(object_id, 'commit').decode()
  lines = iter(commit.splitlines())
  for line in itertools.takewhile(operator.truth, lines):
    key, value = line.split(' ', 1)
    if key == 'tree':
      tree = value
    elif key == 'parent':
      parent = value
    else:
      assert False, f'Unknown field {key}'

  message = ''.join(lines)
  return Commit(tree=tree, parent=parent, message=message)

