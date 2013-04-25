import json
from os import path, replace
from .Heatmap import Heatmap
from .Region import Rectangle, Circle

__dir = path.abspath(path.join(path.dirname(__file__), "..", "..", "statistics"))

class Statistics(object):
  """Statistics is a class that handles the generating of heatmaps
     and statistics JSON for a single player.
     """

  def __init__(self, index, game, config):
    super(Statistics, self).__init__()
    self._heatmap = Heatmap(index, config)
    self._regions = dict()
    for name, subconfig in config["areas"][game]
      if subconfig["type"] == "rect"
        self._regions[name] = Rectangle(subconfig)
      elif subconfig["type"] == "circle":
        self._regions[name] = Circle(subconfig)
      else:
        raise ValueError("Unknown type in config: %s" % value["type"])
    self._index  = index
    self._path = path.join(__dir, "%s.json")

  def generate(self):
    out  = dict()
    path = self._path % now
    for
    with open(path, "w", encoding="utf-8") as fil:
      json.dump(out, fil, indent=4, separators=(',', ': '))
      replace(path, self._path % int(self._index))
