import os
import hashlib

ZIT_DIR = ".zit"

def init():
  os.makedirs(ZIT_DIR, exist_ok=True)
  os.makedirs(f'{ZIT_DIR}/objects', exist_ok=True)

def hash_object(data, type_='blob'):
  # Build the "Git object" in the same format Git uses:"<type>\\x00<contents>"
  obj = type_.encode() + b'\x00' + data
  object_id = hashlib.sha1(obj).hexdigest()
  with open(f'{ZIT_DIR}/objects/{object_id}', "wb") as out:
    out.write(obj)
  #Return the hash (so other parts of your code can reference this object)
  return object_id

def get_object(object_id, expected='blob'):
  with open(f'{ZIT_DIR}/objects/{object_id}', "rb") as f:
    obj = f.read()

  #split the object into type, the separator(we don't need it) and content
  type_, _, content = obj.partition(b'\x00')

  #decode the type from bytes to string so that we can compare it
  type_ = type_.decode()

  # make sure the object type matches. This helps catch bugs early.
  if expected is not None:
    assert type_ == expected, f'Expected {expected}, got {type_}'
  return content

def set_HEAD(object_id):
  with open(f'{ZIT_DIR}/HEAD', 'w') as f:
    f.write(object_id)

def get_HEAD():
  if os.path.isfile(f'{ZIT_DIR}/HEAD'):
    with open(f'{ZIT_DIR}/HEAD') as f:
      return f.read().strip()