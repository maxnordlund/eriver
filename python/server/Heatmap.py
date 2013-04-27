from os import path, rename
from datetime import datetime, timedelta
from TimeList import TimeList
import Image
import math

_dir = path.abspath(path.join(path.dirname(__file__), "..", "..", "heatmaps"))

class Heatmap(TimeList):
  """This represents a heat map."""
  
  def __init__(self, index, config, dir_path=_dir):
    TimeList.__init__(self)
    self._duration = timedelta(minutes=5)
    self._index    = index
    self._path     = path.join(dir_path, "%s.png")
    self._width    = config["width"] if config.has_key("width") else 1024
    self._height   = config["height"] if config.has_key("height") else 768
    self._color    = tuple(config["color"]) if config.has_key("color") else (0, 0, 0)

  def generate(self):
    #heat    = [[0 for x in range(self._width)] for y in range(self._height)]
    heat    = [[0 for y in range(self._height)] for x in range(self._width)]
    
    print "Height %d, Width %d"%(len(heat[0]),len(heat))
    maximum = 1
    buf     = bytearray()
    now     = datetime.now()
    before  = now - self._duration
    path    = self._path % now
    if(len(self)>0):
      print "before %s, first %s"%(before,self._list[0].timestamp)
    data    = self[before:now]
    limit_radius  = 25
    center  = 50.0 # Constant that wont affect the results
    pow_var = 0.5
    del self[:before]
    #TODO check i>3, j>3
    for point in data:
      cx = int(point.x * self._width) 
      cy = int(point.y * self._height)
      for dx in range(-limit_radius,limit_radius):
        for dy in range(-limit_radius,limit_radius):
          px = cx + dx
          py = cy + dy
          if 0 <= px < self._width and 0 <= py < self._height:
            if math.sqrt((dx**2 + dy**2 + 1)) <= limit_radius:
              heat[px][py] += center / math.pow((dx**2 + dy**2 + 1),(pow_var))
              #heat[px][py] += center / (limit_radius+1 - math.pow((dx**2 + dy**2 + 1),(pow_var)))

    for _,_,element in self._walk(heat):
      maximum = max(maximum, element)
    
    """
    # Max stuffs
    for element in self._walk(heat):
      buf.extend(self._color + (int(255 * element / maximum),))

    image = Image.frombuffer("RGBA", (self._width, self._height), buffer(buf), "raw", "RGBA", 0, 1)
    
    """
    # Daniel stuffs
    image = Image.new("RGBA",(self._width,self._height))
    canvas = image.load()
    for x, y, element in self._walk(heat):
      #print self._color + (int(255*element/maximum),)
      canvas[x,y] = self._color + (int(255 * element / maximum),)
    del canvas #TODO maybe clean up 
    
    print("Saving Heatmap")
    with open(path, "wb") as fil:
      image.save(fil, "png")
      rename(path, self._path % int(self._index))
    print("Heatmap Done!")

  def _walk(self, heat):
    for x in range(self._width):
      for y in range(self._height):
        yield x, y, heat[x][y]
