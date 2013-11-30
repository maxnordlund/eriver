import json
from multiprocessing import Process, Queue, Value
from network import TCPHandler
from datetime import datetime, timedelta
import sys, os, struct
from Statistics import Statistics
from Heatmap import Heatmap
from Database import Database
from ctypes import c_bool

def parse_JSON(filename):
  with open(filename) as f:
    return dict(json.load(f))

def debug(msg, isLogging):
  if isLogging.value:
    sys.stdout.write("\n" + msg + "\n>> ")
    sys.stdout.flush()

def _generate_stats(queue, index, player_name, game, ratio, path, isLogging):
  config = parse_JSON(os.path.join(path,"%s.json"%game))
  subconfig = config[ratio]
  #stats = Statistics(index, config[ratio], os.path.join(path,"statistics"))
  stats = Statistics(index, player_name, config[ratio], os.path.join(path,"..","..","statistics"))
  
  while True:
    while not queue.empty():
      etdata = queue.get()
      x = etdata[1]
      y = etdata[2]
      #timestamp = datetime.utcfromtimestamp(etdata[2]) TODO
      timestamp = datetime.now()
      stats[timestamp] = (x,y)
    
    debug("Generating stats", isLogging)
    stats.generate()
    debug("Done stats generation", isLogging)

def start_stats(queue, index, player_name, game, ratio, path, isLogging):
  stats_args = (queue, index, player_name, game, ratio, path, isLogging)
  stats = Process(target=_generate_stats, args=stats_args)
  stats.start()

  return stats

def _generate_heatmap(queue, index, path, isLogging):
  config = parse_JSON(os.path.join(path,"heatmap.json"))
  #Get subconfig from heatmap according to args screen resolution TODO
  #heatmap = Heatmap(index, config, os.path.join(path,"heatmaps"))
  heatmap = Heatmap(index, config, os.path.join(path,"..","..","heatmaps"))

  while True:
    while not queue.empty():
      etdata = queue.get()
      x = etdata[1]
      y = etdata[2]
      #timestamp = datetime.utcfromtimestamp(etdata[2])
      timestamp = datetime.now()
      heatmap[timestamp] = (x,y)
    
    debug("Generating heatmap", isLogging)
    heatmap.generate()
    debug("Done heatmap generation", isLogging)

def start_heatmap(queue, index, path, isLogging):
  heatmap_args = (queue, index, path, isLogging)
  heatmap = Process(target=_generate_heatmap, args=heatmap_args)
  heatmap.start()

  return heatmap

def _generate_match(queue, index, player_name, game, ratio, path, isRunning):
  if not os.path.exists(os.path.join(path, "..", "..", "matches")):
    os.mkdir(os.path.join(path, "..", "..", "matches"))

  dir_path = os.path.join(path, "..","..","matches", player_name)
  if not os.path.exists(dir_path): 
    os.mkdir(dir_path)

  heatmapConfig = parse_JSON(os.path.join(path,"heatmap.json"))
  heatmap = Heatmap(index, heatmapConfig, dir_path)

  heatmap._duration = timedelta(weeks=52)

  statsConfig = parse_JSON(os.path.join(path,"%s.json"%game))
  subconfig = statsConfig[ratio]
  stats = Statistics(index, player_name, statsConfig[ratio], dir_path)
  
  for region in stats._regions.itervalues():
    region._duration = timedelta(weeks=52)
  
  while isRunning.value:
    while not queue.empty():
      etdata = queue.get()
      x = etdata[1]
      y = etdata[2]
      #timestamp = datetime.utcfromtimestamp(etdata[2])
      timestamp = datetime.now()
      heatmap[timestamp] = (x,y)
      stats[timestamp] = (x,y)

  heatmap.generate()
  stats.generate()


def start_match(queue, index, player_name, game, ratio, path, isMatchRunning):
  match_args = (queue, index, player_name, game, ratio, path, isMatchRunning)
  match = Process(target=_generate_match, args=match_args)
  match.start()

  return match

def _listen(addr, queues, isLogging):
  #isLogging = True
    debug("Starting client on addr %s, and host %d"%(addr[0],addr[1]), isLogging)
    tcphandler = TCPHandler(addr,None,False)
    debug("Past tcp handler", isLogging)
    with tcphandler:
        tcphandler.send(struct.pack("!B2dq", 1, 0, 0, 0))
        data = tcphandler.recieve(2)
        (cmd, name) = struct.unpack("!2B", data)
        debug(("Connected to Eyetracker %d" % name), isLogging)
        
        while True:
            data = tcphandler.recieve(25)
            debug("Data Recieved!", isLogging)
            if len(data) < 25:
                continue
            etdata = struct.unpack("!B2dq", data)
            
            debug(("ETData %s" % str(etdata)), isLogging)
            for queue in queues:
              queue.put(etdata) # Put on queue

def start_network(addr, queues, isLogging):
  net_client_args = (addr, queues, isLogging)
  net_client = Process(target=_listen, args=net_client_args)
  net_client.start()

  return net_client

def spawn(index, game, ratio, path, ip, port, player_name):
  #NOTE name
  index = int(index)
  port = int(port)
  addr = (ip, port)
  queues = [Queue(), Queue(), Queue(), Queue()]
  flags = {
    "loggingStats": Value(c_bool, False),
    "loggingHeatmap": Value(c_bool, False),
    "loggingNet": Value(c_bool, False),
    "matchRunning": Value(c_bool, True)
  }

  children = {
    "stats": start_stats(queues[0], index, player_name, game, ratio, path, flags["loggingStats"]),
    "heatmaps": start_heatmap(queues[1], index, path, flags["loggingHeatmap"]),
    "match": start_match(queues[2], index, player_name, game, ratio, path, flags["matchRunning"]),
    "network": start_network(addr, queues, flags["loggingNet"])
  }
  
  return children, flags

class Match():
  def __init__(self,index, game, ratio, path, ip, port, player_name):
    index = int(index)
    port = int(port)
    addr = (ip, port)
    queues = [Queue(), Queue(), Queue(), Queue()]
    self.flags = {
      "loggingStats": Value(c_bool, False),
      "loggingHeatmap": Value(c_bool, False),
      "loggingNet": Value(c_bool, False),
      "matchRunning": Value(c_bool, True)
    }

    self.children = {
      "stats": start_stats(queues[0], index, player_name, game, ratio, path, self.flags["loggingStats"]),
      "heatmaps": start_heatmap(queues[1], index, path, self.flags["loggingHeatmap"]),
      "match": start_match(queues[2], index, player_name, game, ratio, path, self.flags["matchRunning"]),
      "network": start_network(addr, queues, self.flags["loggingNet"])
    }
  
  def log(self, names):
    for name in names:
      key = "logging" + name.capitalize() 
      if key in self.flags:
        self.flags[key].value = True

  def nolog(self, names):
    for name in names:
      key = "logging" + name.capitalize() 
      if key in self.flags:
        self.flags[key].value = False
   
  def stop(self):
    print "Generating match content"
    self.flags["matchRunning"].value = False
    match_child = self.children.pop("match")

    for child in self.children.itervalues():
      if child.is_alive(): 
        child.terminate()

    match_child.join()
    print "Done generating match content"
      
"""
def put_data_database(queue, index, db, isLogging):
  #BORK
  if(db is None):
    db = "testdb.db"

  database = Database(index, db)
  
  while True:
    while not queue.empty():
      etdata = queue.get()
      x = etdata[1]
      y = etdata[2]
      timestamp = datetime.now()
      database[timestamp] = (x,y)
    
    database.generate()
"""
