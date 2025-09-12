import os
import hashlib

ZIT_DIR = ".zit"

def init():
  os.makedirs(ZIT_DIR, exist_ok=True)
  os.makedirs(f'{ZIT_DIR}/objects', exist_ok=True)

def hash_object(data):
  object_id = hashlib.sha1(data).hexdigest()
  with open(f'{ZIT_DIR}/objects/{object_id}', "wb") as out:
    out.write(data)
  #Return the hash (so other parts of your code can reference this object)
  return object_id

def get_object(object_id):
  with open(f'{ZIT_DIR}/objects/{object_id}', "rb") as f:
    return f.read()