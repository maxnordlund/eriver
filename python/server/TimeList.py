from datetime import datetime

class Node(object):
  """This is a coordinate node for the TimeList class."""

  def __init__(self, timestamp, value):
    self.__slots__ = [ "x", "y", "timestamp" ]
    self.x, self.y = value
    self.timestamp = timestamp

  def __lt__(self, other):
    return self.timestamp < other

  def __le__(self, other):
    return self.timestamp <= other

  def __eq__(self, other):
    return self.timestamp == other

  def __ne__(self, other):
    return self.timestamp != other

  def __gt__(self, other):
    return self.timestamp > other

  def __ge__(self, other):
    return self.timestamp >= other

  def __str__(self):
    return "x = %d, y = %d, timestamp = %s" % (self.x, self.y, self.timestamp)

class TimeList(object):
  """TimeList is a class in which you store coordinates by timestamp.

     You can access a single coordinate or a slice of coordinates
     using the closest timestamps. This is done in O(log n)."""

  def __init__(self):
    self._list = list()

  def __len__(self):
    return len(self._list)

  def _slice(self, key):
    if type(key) is slice:
      start = self.index(key.start) if key.start is not None else None
      stop  = self.index(key.stop) if key.stop is not None else None
      step  = self.index(key.step) if key.step is not None else None
      return slice(start, stop, step)
    elif type(key) is datetime:
      return self.index(key)
    else:
      return key

  def __getitem__(self, key):
    return self._list[self._slice(key)]

  def __setitem__(self, key, value):
    return self._list.insert(self._slice(key), Node(key, value))

  def __delitem__(self, key):
    del self._list[self._slice(key)]

  def index(self, key, start=0, stop=None):
    """This returns an opaque index for the supplied date time stamp.
       """
    if len(self._list) == 0 or self._list[0] > key:
      return 0
    elif self._list[-1] < key:
      return len(self)

    stop    = len(self) - 1 if stop is None else stop
    middle  = (stop + start) // 2
    element = self._list[middle]
    if element == key:
      return middle
    elif start == stop:
      #raise ValueError("%s is not in list" % str(key))
      return middle
    elif element > key:
      return self.index(key, start, middle - 1)
    elif element < key:
      return self.index(key, middle + 1, stop)
    else:
      raise ValueError("%s is not in list" % str(key))
