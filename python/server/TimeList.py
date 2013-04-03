class Node(object):
  """This is a coordinate node for the TimeList class."""

  def __init__(self, timestamp, value):
    self.__slots__ = [ "x", "y", "timestamp" ]
    self.x         = value.x
    self.y         = value.y
    self.timestamp = timestamp

  def __lt__(self, other):
    return self.timestamp < other.timestamp

  def __le__(self, other):
    return self.timestamp <= other.timestamp

  def __eq__(self, other):
    return self.timestamp == other.timestamp

  def __ne__(self, other):
    return self.timestamp != other.timestamp

  def __gt__(self, other):
    return self.timestamp > other.timestamp

  def __ge__(self, other):
    return self.timestamp >= other.timestamp

class TimeList(object):
  """TimeList is a class in which you store coordinates by timestamp.

     You can access a single coordinate or a slice of coordinates
     using the closest timestamps. This is done in O(log n)."""

  def __init__(self):
    self._list = list()

  def __len__(self):
    return len(self._list)

  def _slice(self, key):
    if type(key) is slice
      start = self.index(key.start) if key.start is not None else None
      stop  = self.index(key.stop) if key.stop is not None else None
      step  = self.index(key.step) if key.step is not None else None
      return slice(start, stop, step)
    else
      return self.index(key)

  def __getitem__(self, key):
    return self._list[self._slice(key)]

  def __setitem__(self, key, value):
    node = Node(key, value)
    self._list.append(node)
    return node

  def __delitem__(self, key):
    del self._list[self._slice(key)]

  def index(self, value, start=0, stop=None):
    stop    = len(self) - 1 if stop is None else stop
    middle  = (stop+start)//2
    element = self._left[middle]
    if element == value:
      return middle
    elif start == stop:
      raise ValueError("%s is not in list" % str(value))
    elif element > value:
      return self.index(value, start, middle - 1)
    elif element < value:
      return self.index(value, middle + 1, stop)
    else:
      raise ValueError("%s is not in list" % str(value))
