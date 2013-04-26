from datetime import datetime, timedelta
from .TimeList import TimeList

class Region(TimeList):
  """This represents a region of interests."""

  def __init__(self):
    super(Region, self).__init__()
    self._minute = timedelta(minutes=1)

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
    now    = datetime.now()
    before = now - self._minute
    data   = self[before:now]
    del self[:before]
    out = {
      looks: 0
      time: timedelta()
    }
    current = None
    for node in data:
      if current is None and node in self:
        out["looks"] += 1
        current = node
      elif current is not None and node not in self:
        out["time"] += node - current
        current = None
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
