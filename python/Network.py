import asyncore, socket

class Network(asyncore.dispatcher):
  """This is a TCP handler."""

  def __init__(self, address=('localhost', 3031)):
    super(Network, self).__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
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
