from network import TCPHandler
from socket import error
import logging
from threading import (Thread, Lock)

from MockTracker import MockTracker

import struct
import datetime

LOG_FILENAME = 'eriver.log'
logging.basicConfig(filemode='w', filename=LOG_FILENAME,level=logging.INFO)

def enum(**enums):
    return type('Enum', (), enums)

cmds = enum(GETPOINT=1, STARTCAL=2, ADDPOINT=3, CLEAR=4, ENDCAL=5, UNAVALIABLE=6, NAME=7, FLASH_KLUDGE=60, OST=80, TEAPOT=90)
lengths = enum(COMMAND=1, GETPOINT=24, STARTCAL=8, ADDPOINT=16, NAME=1, OST=4, TEAPOT=1)

class ConnHandler(Thread):
    
    def __init__(self, conn, addr, server):
        global cmds

        self.server = server
        self.logger = logging.getLogger("ConnHandler%s" % str(addr))
        self.conn = conn
        self.addr = addr
        self.listen = False
        self.stop = False

        self.protocol = {
            cmds.GETPOINT: self.getPoint,
            cmds.STARTCAL: self.startCal,
            cmds.ADDPOINT: self.addPoint,
            cmds.CLEAR: self.clearCal,
            cmds.ENDCAL: self.endCal,
            cmds.UNAVALIABLE: self.unavaliable,
            cmds.NAME: self.sendName,
            cmds.OST: self.sayCheese,
            cmds.TEAPOT: self.IAmATeapot,
            #cmds.FLASH_KLUDGE: self.getPoint

            }#TODO Fill with functions for great justice.

        Thread.__init__(self)

    def __hash__(self):
        return hash(self.addr)

    def __str__(self):
        return str(self.addr)

    def run(self):
        global cmds
        global lengths

        self.logger.info("Starting new thread!")
        self.sendName()
        while not (self.stop or self.server.shutdown):
            try:
                data = self.conn.recieve(lengths.COMMAND)
            except error:
                self.panic("Error on recieve of command.")
                return
                
            if len(data) < lengths.COMMAND:
               continue
            command = struct.unpack("!B", data)[0]
            self.logger.info("Says %d" % (command))
            self.protocol.get(command, self.unavaliable)()

    
    # Panic method.
    # If an error is found on the network, call this and let it handle it "gracefully".
    def panic(self, what="FAT"):
        self.logger.info("O NOES! FRIEND %s DONT LEIK ME ANYMORE!\n\t IT SAID I WAS %s!" % (str(self), what))
        self.server.handlersLock.acquire()
        try:
            del self.server.handlers[self]
        except KeyError:
            self.logger.warning("Tried to delete client %s that did not exist" % str(self))
        self.server.handlersLock.release()
        self.stop = True
        

    def send(self, data):
        try:
            self.conn.send(data)
        except error:
            self.panic("Error on send of %s" % data)

    # Sends a signal to the other side, that the command they attempted to use is unavailiable at this time.
    # Panics if error if found on send.
    def unavaliable(self):
        self.send(struct.pack("!B", cmds.UNAVALIABLE))

    def getPoint(self):
        global lengths
        try:
            self.conn.recieve(lengths.GETPOINT)
        except error:
            self.panic("Error on read of getPoint")
            return
        self.listen = not self.listen

    def startCal(self):
        global lengths
        self.logger.info("STARTCAL")
        try:
            data = self.conn.recieve(lengths.STARTCAL)
        except error:
            self.panic("Error on read of startCal")
            return

        if not len(data) == lengths.STARTCAL:
            self.logger.error("Not correct length read for STARTCAL")
            return
        angle = struct.unpack("!d", data)[0]
        self.logger.debug("Angle: %d" % angle)
        if self.server.eyetracker.startCalibration(angle):
            self.send(struct.pack("!Bd", cmds.STARTCAL, angle))
        else:
            self.unavaliable()

    def addPoint(self):
        global lengths
        global cmds
        data = ""
        try:
            data = self.conn.recieve(lengths.ADDPOINT)
        except error:
            self.panic("Error on read of addPoint")
            return

        if not len(data) == lengths.ADDPOINT:
            self.logger.error("Not correct length read for ADDPOINT")
            return
        point = struct.unpack("!2d", data)
        if self.server.eyetracker.addPoint(point[0], point[1]):
            self.send(struct.pack("!B", cmds.ADDPOINT) + data)

        else:
            self.unavaliable()

    def clearCal(self):
        if self.server.eyetracker.clearCalibration():
            self.send(struct.pack("!B", cmds.CLEARCAL))
        else:
            self.unavaliable()

    def endCal(self):
        if self.server.eyetracker.endCalibration():
            self.send(struct.pack("!B", cmds.ENDCAL))
        else:
            self.unavaliable()

    def sendName(self):
        self.send(struct.pack("!2B", cmds.NAME, self.server.eyetracker.name))

    def sayCheese(self):
        self.send("Appenzeller")

    def IAmATeapot(self):
        self.send("418 I am a teapot!")

    def Flash_Kludge(self):
        try:
            data = self.conn.recieve(lengths.FLASH_KLUDGE)
        except error:
            self.panic("Error on read of flashkludge")

        self.send('<?xml version="1.0"?><cross-domain-policy><allow-access-from domain="*" to-ports="*" ></cross-domain-policy>\0')

class ETServer(object):
    def __init__(self, addr, name="ETServer"):
        self.shutdown = False # A way for any part of the server to give a shutdown signal
        self.handlers = dict()# All the handlers of the server
        self.handlersLock = Lock()# A lock to regulate when parts can use the handlers.
        self.eyetracker = MockTracker(self.sendData) #We need a tracker aswell.
        self.logger = logging.getLogger(name) # A logger is good to have
        
        self.serverSocket = TCPHandler(addr, None, True) # Create a server socket for listening to connection attempts

    def sendData(self, etevent):
        #logger.debug("Handlers: %s" % str(handlers))
        #Do not block. This leads to lost events when clients disconnect, but hey, better than having the server lag behind...
        if self.handlersLock.acquire(False):
            for h in self.handlers:
                self.logger.debug(str(h) + str(h.listen))
                if h.listen:
                    h.send(struct.pack("!B2dq", cmds.GETPOINT, etevent.x, etevent.y, etevent.timestamp)) #This might go bad if one handler blocks.
            self.handlersLock.release()

    def start(self):
        if not self.eyetracker.enable():
            self.logger.critical("WAT? Eye tracker not enablable?")
        self.logger.debug("Active? %s" % str(self.eyetracker.active))
        
        with self.serverSocket: # Start listen and make sure it is closed!
            while not self.shutdown: #Loop until we recive signal of shutdown
                try:
                    conn, addr = self.serverSocket.accept() #Blockingly accept connections
                    self.logger.info("\t\t\tFRIEND! AWSUM THX!")
                    h = ConnHandler(conn, addr, self) #Take new connection and fork off a handler
                    self.handlersLock.acquire() #We do not want the iterator to be mad at us for modifying the dictionary during its run.
                    self.handlers[h] = True #Put it in dictionary for safe storage.
                    self.handlersLock.release() # And release!
                    h.start() #And kick it away!
                except (error, KeyboardInterrupt) as e:
                    self.shutdown = True #O NOES!
                    for h in self.handlers:
                        h.join() #CAN I HAS SYNCZ?

                    if isinstance(e, error):
                        self.logger.critical("Unhandled network error in listener.")
                        raise
                    else:
                        self.logger.warning("Server stopped by user.")
                

        self.logger.info("\tPLZ CLOSE EVERYTHING!")
        

if __name__ == "__main__":

    import sys, traceback
    
    addr = ("0.0.0.0", 3031)
    logging.info("HAI")
    logging.info("CAN I HAS NETWORK?")
    logging.info("PLZ LISTEN 2 TCP " + str(addr) + "?")
    logging.info("\tAWSUM THX")
    logging.info("\t\tDO_STUFFS!")
    try:
        ETServer(addr).start()

    except error:
        logging.info("\tO NOES")
        logging.info("\t\tPANIC!")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.info("\t\tLOOKZ! KITTY!")
        logging.error("KITTY! IT HID " + datetime.datetime.now().isoformat(' '))
        logging.error("Type:%s \t Value: %s\n%s" % (str(exc_type), str(exc_value), str(exc_traceback)))
        
    finally:
        logging.info("KTHXBYE!")


    
