"""
Server main

command line arguments:
  index,  e.g 1
  game,   e.g starcraft2
  ratio,  e.g 16:9
  path,   e.g ./
  ip,     e.g 10.76.155.133
  port,   e.g 3031

"""
import json
from multiprocessing import Process, Queue, Value
from network import TCPHandler
from datetime import datetime, timedelta
import sys, os, struct
from Statistics import Statistics
from Heatmap import Heatmap
from Database import Database
from ctypes import c_bool
from children import Match

current_match = None

def log(args):
  global current_match
  if current_match is not None:
    current_match.log(args)

def nolog(args):
  global current_match
  if current_match is not None:
    current_match.nolog(args)

def start(args):
  global current_match
  if current_match is not None:
    current_match.stop()
  current_match = Match(*(sys.argv[1:] + args))

def stop(args):
  global current_match
  if current_match is not None:
    current_match.stop()
    current_match = None

commands = {
  "log": log,
  "nolog": nolog,
  "start": start,
  "stop": stop,
  "kill": stop
}

if __name__ == "__main__":
  """
  index = int(sys.argv[1]) 
  game  = sys.argv[2] 
  ratio = sys.argv[3] 
  path  = sys.argv[4] 
  ip    = sys.argv[5] 
  port  = int(sys.argv[6]) 
  addr  = (ip,port)
  """
  
  while True:
    try:
      cmd = raw_input(">> ").split(" ")
    except (KeyboardInterrupt, EOFError): 
      stop([])
      print
      sys.exit(0)

    else:
      if(cmd[0] in commands):
        commands[cmd[0]](cmd[1:])
