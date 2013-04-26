class Handler(asyncore.dispatcher_with_send):
  """This is a handler for a single player."""
  #TODO skriv om eller skriv klart här!
  def __init__(self, index, config):
    super(Handler, self).__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self._regions = list()
    self._heatmap = Heatmap(index, config.heatmap)
    # self._database = Database(index)
    for region in config.areas
      if region.type == "rect"
        self._regions.append(Rectangle(index, region))
      elif region.type == "circle"
        self._regions.append(Circle(index, region))

  def start(self, address=('localhost', 3031)):
    self.connect(address)

  def handle_connect(self):
    pass

  def handle_close(self):
    self.close()

  def handle_read(self):
    print self.recv(8192)

  def writable(self):
    return (len(self.buffer) > 0)

  def handle_write(self):
    sent = self.send(self.buffer)
    self.buffer = self.buffer[sent:]
