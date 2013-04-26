import json
from os import path, replace
from .Heatmap import Heatmap
from .Region import Rectangle, Circle
from datetime import datetime

__dir = path.abspath(path.join(path.dirname(__file__), "..", "..", "statistics"))

class Statistics(object):
  """Statistics is a class that handles the generating of heatmaps
     and statistics JSON for a single player.
     """

  def __init__(self, index, config, dir_path=__dir):
    super(Statistics, self).__init__()
    self._regions = dict()
    for name, subconfig in config
      if subconfig["type"] == "rect"
        self._regions[name] = Rectangle(subconfig)
      elif subconfig["type"] == "circle":
        self._regions[name] = Circle(subconfig)
      else:
        raise ValueError("Unknown type in config: %s" % value["type"])
    self._index = index
    self._path  = path.join(dir_path, "%s.json")):

  def __setitem__(self, key, value):
    for region in self._regions.values():
      region[key] = value

  def generate(self):
    out = dict()
    now = datetime.now()
    file_path = self._path % now
    for name, region in self._regions:
      out[name] = region.generate()
    with open(path, "w", encoding="utf-8") as fil:
      json.dump(out, fil, indent=4, separators=(',', ': '))
      replace(path, self._path % int(self._index))
