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

  def __init__(self, index, config, dir_path=_dir):
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
    
    with open(file_path, "w") as fil:
      json.dump(out, fil, indent=4, separators=(',', ': '))
      rename(file_path, self._path % int(self._index))
