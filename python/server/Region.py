from datetime import datetime, timedelta
from .TimeList import TimeList

class TemporalNode(object):
  """This is a coordinate node for the Region class."""

  def __init__(self, begin, value):
    self.__slots__ = [ "x", "y", "begin", "end" ]
    self.x     = value.x
    self.y     = value.y
    self.begin = begin
    self.end   = datetime.max

  def len(self):
    return self.end - self.begin if self.end is not datetime.max else 0

  def __lt__(self, timestamp):
    return self.begin < timestamp

  def __le__(self, timestamp):
    return self.begin <= timestamp

  def __eq__(self, timestamp):
    return timestamp in self

  def __ne__(self, timestamp):
    return timestamp not in self

  def __contains__(self, timestamp):
    return self.begin <= timestamp <= self.end

  def __gt__(self, timestamp):
    return self.end > timestamp

  def __ge__(self, timestamp):
    return self.end >= timestamp

class Region(TimeList):
  """This represents a region of interests."""

  def __init__(self):
    super(Region, self).__init__()
    self._current = None
    self._minute  = timedelta(minutes=1)

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
    out    = dict()
    now    = datetime.now()
    before = now - self._minute
    data   = self[before:now]
    del self[:before]
    out["looks"] = len(data)
    out["time"]  = timedelta()
    for delta in data:
      out["time"] += delta.len()
    return out

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
