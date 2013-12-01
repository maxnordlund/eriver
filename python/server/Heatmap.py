from os import path, rename
from datetime import datetime, timedelta
from TimeList import TimeList
from PIL import Image
import math

_dir = path.abspath(path.join(path.dirname(__file__), "..", "..", "heatmaps"))

class Heatmap(TimeList):
  """This represents a heat map."""
  
  def __init__(self, index, config, dir_path=_dir):
    TimeList.__init__(self)
    self._duration = timedelta(minutes=5)
    self._index    = index
    self._path     = path.join(dir_path, "%s.png")
    self._width    = config["width"] if "width" in config else 1024
    self._height   = config["height"] if "height" in config else 768
    self._color    = tuple(config["color"]) if "color" in config else (0, 0, 0)

  def generate(self):
    heat    = [[0 for y in range(self._height)] for x in range(self._width)]
    maximum = 1
    buf     = bytearray()
    now     = datetime.now()
    before  = now - self._duration
    path    = self._path % now
    data    = self[before:now]
    limit_radius  = 25
    center  = 50.0 # Constant that wont affect the results
    pow_var = 0.5
    del self[:before]
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

    for _,_,element in self._walk(heat):
      maximum = max(maximum, element)
    
    image = Image.new("RGBA",(self._width,self._height))
    canvas = image.load()
    for x, y, element in self._walk(heat):
      canvas[x,y] = self._color + (int(255 * element / ((maximum+1)/1.5)),)
    del canvas 
        
    with open(path, "wb") as fil:
      image.save(fil, "png")
      rename(path, self._path % int(self._index))

  def _walk(self, heat):
    for x in range(self._width):
      for y in range(self._height):
        yield x, y, heat[x][y]
