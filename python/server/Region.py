import os
import json
import io
from datetime import datetime, timedelta
from .TimeList import TimeList

__dir = os.path.dirname(os.path.join(os.path.abspath(__file__), "..", "..", "statistics")

class TemporalNode(object):
  """This is a coordinate node for the Region class."""

  def __init__(self, begin, value):
    self.__slots__ = [ "x", "y", "begin", "end" ]
    self.x     = value.x
    self.y     = value.y
    self.begin = begin
    self.end   = datetime.max

  def __len__(self):
    return self.end - self.begin if self.end is not datetime.max else timedelta()

  def __lt__(self, other):
    return self.begin < other.timestamp

  def __le__(self, other):
    return self.begin <= other.timestamp

  def __eq__(self, other):
    return other.timestamp in self

  def __ne__(self, other):
    return other.timestamp not in self

  def __contains__(self, item):
    return self.begin <= item.timestamp <= self.end

  def __gt__(self, other):
    return self.end > other.timestamp

  def __ge__(self, other):
    return self.end >= other.timestamp

class Region(TimeList):
  """This represents a region of interests."""

  def __init__(self):
    TimeList.__init__(self)
    self._duration = timedelta(minutes=1)

  def __contains__(self, item):
    raise NotImplementedError("Must be overridden in subclass")

  def generate(self):
    now    = datetime.now()
    before = now - self._duration
    data   = self[before:now]
    del self[:before]
    out = {
      "looks": 0,
      "time": timedelta()
    }
    current = None
    for node in data:
      if current is None and node in self:
        out["looks"] += 1
        current = node
      elif current is not None and node not in self:
        out["time"] += node - current
        current = None

    out["time"] = str(out["time"])
    return out

  def __setitem__(self, key, value):
    if self._current is None and value in self:
      self._current = TemporalNode(datetime.now(), value)
      self._list.append(self._current)
    elif self._current is not None and value not in self
      self._current.end = datetime.now()
      self._current = None
    return self._current

  def generate(self):
    out  = dict()
    now  = datetime.now()
    path = self._path + str(now)
    data = self[now-self._minute:now]
    del self[:now-self._minute]
    out["looks"] = len(data)
    out["time"]  = timedelta()
    for delta in map(len, data):
      time += delta
    with open(, "w", encoding="utf-8") as fil:
      json.dump(out, fil, indent=4, separators=(',', ': '))

class Rectangle(Region):
  """This represents a rectangular region of interests."""

  def __init__(self, config):
    super(Rectangle, self).__init__()
    self.top    = config["top"]
    self.right  = config["right"]
    self.bottom = config["bottom"]
    self.left   = config["left"]

  def __contains__(self, item):
    return self.top <= item.y <= self.bottom and self.left <= item.x <= self.right

class Circle(Region):
  """This represents a circular region of interests."""

  def __init__(self, config):
    super(Circle, self).__init__()
    self.cx     = config["x"]
    self.cy     = config["y"]
    self.radius = config["radius"]**2

  def __contains__(self, item):
    return ((item.x - self.cx)**2 + (item.y - self.cy)**2) <= self.radius
