from . import data
import os

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
  tree = data.get_object(object_id, 'tree')
  for entry in tree.decode().splitlines():
    type_, object_id, name = entry.split(' ', 2)

    # Yield this entry as a tuple (type, object_id, name).
    # Using 'yield' turns this function into a generator:
    # - It returns one entry at a time instead of building a full list.
    # - The function pauses here and resumes on the next iteration.
    yield type_, object_id, name

