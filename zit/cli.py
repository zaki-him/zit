import argparse
import os
import sys
from . import data
from . import base

def parse_args():
  # Create the main argument parser
  parser = argparse.ArgumentParser()

  #This allows us to have multiple commands like init, commit, etc
  commands = parser.add_subparsers(dest="command") #the chosen command will be stored in args.command
  commands.required = True

  # Create a parser for the "init" command
  init_parser = commands.add_parser("init")

  # When the "init" command is used, set args.func to the "init" function
  init_parser.set_defaults(func=init)

  hash_object_parser = commands.add_parser("hash-object")
  hash_object_parser.set_defaults(func=hash_object)
  hash_object_parser.add_argument("file")

  cat_file_parser = commands.add_parser("cat-file")
  cat_file_parser.set_defaults(func=cat_file)
  cat_file_parser.add_argument("object")

  write_tree_parser = commands.add_parser("write-tree")
  write_tree_parser.set_defaults(func=write_tree)

  read_tree_parser = commands.add_parser("read-tree")
  read_tree_parser.set_defaults(func=read_tree)
  read_tree_parser.add_argument('tree')

  commit_parser = commands.add_parser("commit")
  commit_parser.set_defaults(func=commit)
  commit_parser.add_argument("-m", "--message", required=True)

  return parser.parse_args()

def init(args):
  data.init()
  print(f'Initialized empty zit repository in {os.getcwd()}\\{data.ZIT_DIR}')

def hash_object(args):
  with open(args.file, "rb") as f:
    print(data.hash_object(f.read()))

def cat_file(args):
  # Flush any pending text output before we start writing binary data.
  # This prevents any mix-up between regular printed text and raw bytes.
  sys.stdout.flush()

  # Write the object's raw bytes directly to stdout's binary buffer.
  # Using .buffer ensures we don't accidentally try to decode the bytes as text.
  # This way, the exact contents of the stored object are output as-is.
  sys.stdout.buffer.write(data.get_object(args.object, expected=None))
  
def write_tree(args):
  print(base.write_tree())

def read_tree(args):
  base.read_tree(args.tree)

def commit(args):
  print(base.commit(args.message))

def main():
  # Call the parse_args() function to process command-line input
  args = parse_args()

  # Call the function that was set by the subcommand (e.g, if the command was init then the function init() gets called)
  args.func (args)