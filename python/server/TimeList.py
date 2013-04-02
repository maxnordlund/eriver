class Node(object):
  """Node is a coordinate node for the TimeList class."""

  def __init__(self, x, y, timestamp):
    self.__slots__ = [ "x", "y", "timestamp" ]
    self.x = x
    self.y = y
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
     using the closests timestamps. This is done in O(log n)."""

  def __init__(self):
    self._Node = Node
    self._list = list()

  def index(self, value, i=0, j=None):
    j = len(self) - 1 if j is None else j
    if i >= j:
      raise ValueError
    k = (j+i)//2
    middle = self._left[k]
    if value < middle:
      return self.index(value, i, k)
    elif middle < value:
      return self.index(value, k, j)
    else:
      pass


  def __len__(self):
    return len(self._list)

  def __getitem__(self, key):

  def __setitem__(self, key, value):

  def __delitem__(self, key):


