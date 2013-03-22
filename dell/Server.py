from network import TCPHandler
from socket import error
from threading import (Thread, Lock)

from MockTracker import MockTracker

import struct
import datetime

global shutdown
global handlers
global handlersLock

shutdown = False
handlers = dict()
handlersLock = Lock()

def enum(**enums):
    return type('Enum', (), enums)

cmds = enum(GETPOINT=1, STARTCAL=2, ADDPOINT=3, CLEAR=4, ENDCAL=5, UNAVALIABLE=6, NAME=7, OST=80, TEAPOT=90)
lengths = enum(COMMAND=1, GETPOINT=24, STARTCAL=8, ADDPOINT=16, NAME=1, OST=4, TEAPOT=1)

class ConnHandler(Thread):
    
    def __init__(self, conn, addr):
        global cmds
        
        self.conn = conn
        self.addr = addr
        self.listen = False
        self.stop = False

        self.protocol = {
            cmds.GETPOINT: self.getPoint,
            #cmds.STARTCAL: self.startCal,
            #cmds.ADDPOINT: self.addPoint,
            #cmds.CLEAR: self.clearCal,
            #cmds.ENDCAL: self.endCal,
            cmds.UNAVALIABLE: self.unavaliable,
            cmds.NAME: self.sendName,
            cmds.OST: self.sayCheese,
            cmds.TEAPOT: self.IAmATeapot,

            }#TODO Fill with functions for great justice.

        Thread.__init__(self)

    def __hash__(self):
        return hash(self.addr)

    def run(self):
        global name
        global cmds
        global lengths
        global shutdown

        print("Starting new thread!")
        self.sendName()
        while not self.stop or not shutdown:
            try:
                data = self.conn.recieve(lengths.COMMAND)
            except error:
                self.panic()
                
            if len(data) < lengths.COMMAND:
               continue
            command = struct.unpack("!B", data)[0]
            self.protocol.get(command, self.unavaliable)()

    
    # Panic method.
    # If an error is found on the network, call this and let it handle it "gracefully".
    def panic(self):
        global handlers
        global handlersLock

        handlersLock.acquire()
        del handlers[self]
        handlersLock.release()
        self.stop = True

    def send(self, data):
        try:
            self.conn.send(data)
        except error:
            self.panic()

    # Sends a signal to the other side, that the command they attempted to use is unavailiable at this time.
    # Panics if error if found on send.
    def unavaliable(self):
        try:
            self.conn.send(struct.pack("!B", cmds.UNAVALIABLE))
        except error:
            self.panic()

    def getPoint(self):
        global lengths
        try:
            self.conn.recieve(lengths.GETPOINT)
        except:
            panic()
        self.listen = not self.listen

    def startCal(self):
        global eyetracker
        global lengths
        data = ""
        try:
            data = self.conn.recieve(lengths.STARTCAL)
        except:
            panic()

        if not len(data) == lengths.STARTCAL
        angle = struct.unpack("!q", data)[0]
        if not eyetracker.startCalibration(angle):
            self.unavaliable()

    def addPoint(self):
        global eyetracker
        if not eyetracker.addPoint():
            self.unavaliable()

    def clearCal(self):
        global eyetracker
        if not eyetracker.clearCalibration():
            self.unavaliable()

    def endCal(self):
        global eyetracker
        if not eyetracker.endCalibration():
            self.unavaliable()

    def sendName(self):
        global eyetracker
        try:
            self.conn.send(struct.pack("!2B", cmds.NAME, eyetracker.name))

        except error:
            self.panic()

    def sayCheese(self):
        try:
            self.conn.send("Appenzeller")
        except error:
            self.panic()

    def IAmATeapot(self):
        try:
            self.conn.send("418 I am a teapot!")
        except error:
            self.panic()

def sendData(etevent):
    global handlers
    global handlersLock
    #print("Handlers: %s\n" % str(handlers))
    #Do not block. This leads to lost events when clients disconnect, but hey, better than having the server lag behind...
    if handlersLock.acquire(False):
        for h in handlers:
            if h.listen:
                h.send(struct.pack("!B2dq", cmds.GETPOINT, etevent.x, etevent.y, etevent.timestamp)) #This might go bad if one handler blocks.
        handlersLock.release()

def startServer(addr):
    global shutdown #Use the global shutdown variable
    global handlers #And the global map of handlers
    global handlersLock 
    global eyetracker #We have a global tracker aswell.
    
    serverSocket = TCPHandler(addr, None, True) # Create a server socket for listening to connection attempts
    eyetracker = MockTracker(sendData) # Connect to the eyetracker

    if not eyetracker.enable():
        print("WAT?")
    print("Active? %s" % str(eyetracker.active))
    
    with serverSocket: # Make sure it is closed!
        while not shutdown: #Loop until we recive signal of shutdown
            try:
                conn, addr = serverSocket.accept() #Blockingly accept connections
                print("FRIEND! AWSUM THX!\n")
                h = ConnHandler(conn, addr) #Take new connection and fork off a handler
                handlersLock.acquire() #We do not want the iterator to be mad at us for modifying the dictionary during its run.
                handlers[h] = True #Put it in dictionary for safe storage.
                handlersLock.release() # And release!
                h.start() #And kick it away!
            except (error, KeyboardInterrupt) as e:
                shutdown = True #O NOES!
                for h in handlers:
                    h.join() #CAN I HAS SYNCZ?

                if isinstance(e, error):
                    raise
            

    print("\tPLZ CLOSE EVERYTHING!")
        

if __name__ == "__main__":

    import sys, traceback
    
    addr = ("0.0.0.0", 3031)
    print("HAI\n")
    print("CAN I HAS NETWORK?\n")
    print("PLZ LISTEN 2 TCP " + str(addr) + "?\n")
    print("\tAWSUM THX\n")
    print("\t\tDO_STUFFS!\n")
    try:
        startServer(addr)

    except:
        print("\tO NOES\n")
        print("\t\tPANIC!\n")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("\t\tLOOKZ! KITTY!")
        try:
            with open("stderr.out", "a") as f:
                f.write("KITTY! IT HID " + datetime.datetime.now().isoformat(' ') + "\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=f)
                f.write("\n\n")
                print("\t\tAWWW.. IT HID IN BOX " + f.name)
        
        except:
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=5)
            print("\t\tAWWW.. IT WANTED TO PLAY...")
        
        
    finally:
        print("KTHXBYE!\n")


    
