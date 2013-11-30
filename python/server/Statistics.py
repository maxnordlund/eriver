import json
from os import path, rename
from Heatmap import Heatmap
from Region import Rectangle, Circle
from datetime import datetime


_dir = path.abspath(path.join(path.dirname(__file__), "..", "..", "statistics"))

class Statistics(object):
  """
  Statistics is a class that handles the generating of heatmaps
  and statistics JSON for a single player.
  """

  def __init__(self, index, player_name, config, dir_path=_dir):
    object.__init__(self)
    self._regions = dict()
    for name, subconfig in config.iteritems():
      if subconfig["type"] == "rect":
        self._regions[name] = Rectangle(subconfig)
      elif subconfig["type"] == "circle":
        self._regions[name] = Circle(subconfig)
      else:
        raise ValueError("Unknown type in config: %s" % value["type"])
    self._index = index
    self._player_name = player_name
    self._path  = path.join(dir_path, "%s.json")

  def __setitem__(self, key, value):
    for region in self._regions.values():
      region[key] = value

  def generate(self):
    out = dict()
    now = datetime.now()
    file_path = (self._path + "-id%s") % (now, int(self._index))
    for name, region in self._regions.iteritems():
      out[name] = region.generate()

    # Warp in dict
    wrapper_out = dict()

    # NOTE Hotfix, DHW13 StarCraft2
    players = self._player_name.split("__vs__")

    if len(players) == 2:
      wrapper_out["player"] = players[self._index-1] # index = 1 -> player[0]
      
      match_round = players[1].split("__nr__") # playerB__nr__1
      if len(match_round) == 2:
        wrapper_out["round"] = match_round[1]
        wrapper_out["player"] = match_round[0] # Second player name updated

    else:
      wrapper_out["player"] = ""
      wrapper_out["round"] = ""
    """ 
    match_round = players[-1].split("__nr__")

    if len(match_round) == 2:
      wrapper_out["round"] = match_round[1]
    else:
      wrapper_out["round"] = ""
    """
    wrapper_out["name"] = self._player_name
    wrapper_out["areas"] = out
    
    with open(file_path, "w") as fil:
      json.dump(wrapper_out, fil, indent=4, separators=(',', ': '))
      rename(file_path, self._path % int(self._index))
