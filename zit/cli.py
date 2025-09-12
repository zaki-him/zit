import argparse
import os
from . import data

def parse_args():
  # Create the main argument parser
  parser = argparse.ArgumentParser()

  #this allowsus to have multiple commands like init, commit, etc
  commands = parser.add_subparsers(dest="command") #the chosen command wil be stored in args.command
  commands.required = True

  # Create a parser for the "init" command
  init_parser = commands.add_parser("init")

  # When the "init" command is used, set args.func to the "init" function
  init_parser.set_defaults(func=init)

  hash_object_parser = commands.add_parser("hash-object")
  hash_object_parser.set_defaults(func=hash_object)
  hash_object_parser.add_argument("file")

  return parser.parse_args()

def init(args):
  data.init()
  print(f'Initialized empty zit repository in {os.getcwd()}\{data.ZIT_DIR}')

def hash_object(args):
  with open(args.file, "rb") as f:
    print(data.hash_object (f.read()))
  

def main():
  # Call the parse_args() function to process command-line input
  args = parse_args()

  # Call the function that was set by the subcommand (e.g, if the command was init then the function init() gets called)
  args.func (args)