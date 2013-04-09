from socket import *

class NetHandler(object):
     def __init__(self, kind, address=('localhost', 3031), blocking=None, listen=False, sock=None):
          if (sock == None):
               self.socket = socket(AF_INET, kind)
          else:
               self.socket = sock
          self.address = address
          self.set_blocking(blocking)
          self._listen = listen
          

     def send(self, data, address=None):
          raise NotImplementedError('You need one of the child classes that implement this method.')

     def recieve(self, size):
          raise NotImplementedError('You need one of the child classes that implement this method.')

     def close(self):
          self.socket.close()

     def set_blocking(self, blocking=0):
          self.blocking = blocking
          self.socket.settimeout(blocking)

     #With statement methods
     def __enter__(self):
          if self._listen:
               self.socket.bind(address)
               self.socket.listen(5)

     def __exit__(self, type, vale, traceback):
          self.close()
    

class UDPHandler(NetHandler):
    def __init__(self, address=('localhost', 3031), blocking=None, listen=False, socket=None):
        super(UDPHandler, self).__init__(SOCK_DRAM, address, blocking, listen, socket)
        
    def send(self, data, address=None):
        if not address == None:
            self.socket.sendto(data, address)
        else:
            self.socket.sendto(data, self.address)

    def recieve(self, size):
        return self.socket.recvfrom(size)
            


class TCPHandler(NetHandler):
    def __init__(self, address=('localhost', 3031), blocking=None, listen=False, sock=None):
        super(TCPHandler, self).__init__(SOCK_STREAM, address, blocking, listen, sock)
        if not listen and sock == None:
             self.socket.connect(address)
           
    def send(self, data):
            self.socket.sendall(data)

    def recieve(self, size):
        return self.socket.recv(size)

    def accept(self):
        conn, addr = self.socket.accept()
        return TCPHandler(addr, self.blocking, False, conn), addr
