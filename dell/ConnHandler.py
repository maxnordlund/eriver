from network import TCPHandler
from socket import error
import logging
from threading import Lock

from MockTracker import MockTracker
from TobiiTracker import AnalyticsTracker as TobiiTracker

import struct
import datetime

def enum(**enums):
    return type('Enum', (), enums)

cmds = enum(GETPOINT=1, STARTCAL=2, ADDPOINT=3, CLEAR=4, ENDCAL=5, UNAVALIABLE=6, NAME=7, FPS=8, FLASH_KLUDGE=60, OST=80, TEAPOT=90)
lengths = enum(COMMAND=1, GETPOINT=24, STARTCAL=8, ADDPOINT=16, NAME=1, FLASH_KLUDGE=22, FPS=4, OST=4, TEAPOT=1)

class ConnHandler():
    
    def __init__(self, conn, addr, et_constructor, name):
        global cmds

        self.tracker = et_constructor(name=name)
        self.name = name
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
            cmds.FPS: self.sendFPS,
            cmds.OST: self.sayCheese,
            cmds.TEAPOT: self.IAmATeapot,
            cmds.FLASH_KLUDGE: self.getPoint

            }#TODO Fill with functions for great justice.

    def __hash__(self):
        return hash(self.addr)

    def __str__(self):
        return str(self.addr)

    def start(self):
        self.logger.debug("Handler started!")
        self.enable_tracker()
        self.tracker.register_onETEvent(self.sendData)
        self.run()
        

    def run(self):
        global cmds
        global lengths

        self.logger.info("Starting new thread!")
        self.sendName()
        while not (self.stop):
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
        else:
            self.logger.critical("Handler was stillborn.")

        self.logger.info("Handler shutting down.")

        

    
    # Panic method.
    # If an error is found on the network, call this and let it handle it "gracefully".
    def panic(self, error=None):
        if error:
            self.logger.error("O NOES! %s" %  error)
            
        def on_disable(res):
            if not res:
                self.logger.critical("Can't disable tracker!")
                
        self.tracker.disable(on_disable)
        self.stop = True
        

    def send(self, data):
        try:
            self.conn.send(data)
        except error:
            self.panic("Error on send of %s" % data)

    def sendData(self, etevent):
        #self.logger.debug("Listening: %s" % self.listen)
        if self.listen:
            #This might go bad if the handler blocks.
            self.send(struct.pack("!B2dq", cmds.GETPOINT, etevent.x, etevent.y, etevent.timestamp))

    def enable_tracker(self):
        lock = Lock() # For syncronization

        def on_enable(res):
            if not res:
                self.logger.critical("WAT? Eye tracker not enablable?")
                self.shutdown = True
            lock.release()

        lock.acquire()
        self.tracker.enable(blocking=True, callback=on_enable)

        lock.acquire()

    # Sends a signal to the other side, that the command they attempted to use is unavailiable at this time.
    # Panics if error if found on send.
    def unavaliable(self):
        self.send(struct.pack("!B", cmds.UNAVALIABLE))


    ###########################
    # PROTOCOL IMPLEMENTATION #
    ###########################

    def getPoint(self):
        global lengths
        try:
            data = self.conn.recieve(lengths.GETPOINT)
        except error:
            self.panic("Error on read of getPoint")
            return
        self.listen = not self.listen
        self.logger.debug("GetPoint: %s" % self.listen)

    def startCal(self):
        global lengths
        
        try:
            data = self.conn.recieve(lengths.STARTCAL)
        except error:
            self.panic("Error on read of startCal")
            return

        if not len(data) == lengths.STARTCAL:
            self.logger.error("Not correct length read for STARTCAL")
            return
        angle = struct.unpack("!d", data)[0]
        

        def on_startcal(res):
            if res:
                self.send(struct.pack("!Bd", cmds.STARTCAL, angle))
            else:
                self.unavaliable()
        
        self.tracker.startCalibration(angle, on_startcal)
        self.logger.debug("StartCalibration Angle: %d" % angle)
        

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

        def on_addpoint(res):
            if res:
                self.send(struct.pack("!B", cmds.ADDPOINT) + data)

            else:
                self.unavaliable()
    
        self.tracker.addPoint(point[0], point[1], on_addpoint)
        self.logger.debug("AddPoint x: %f; y: %f" % point)

    def clearCal(self):
        def on_clear(res):
            if res:
                self.send(struct.pack("!B", cmds.CLEARCAL))
            else:
                self.unavaliable()

        self.tracker.clearCalibration(on_clear)

    def endCal(self):
        def on_end(res):
            if res:
                self.send(struct.pack("!B", cmds.ENDCAL))
            else:
                self.unavaliable()

        self.tracker.endCalibration(on_end)
        
    def sendName(self):
        self.send(struct.pack("!2B", cmds.NAME, self.name))

    def sendFPS(self):
        #self.logger.debug("FPS!")
        try:
            data = self.conn.recieve(lengths.FPS)
        except error:
            self.panic("Error on read of fps")
            return

        if not len(data) == lengths.FPS:
            self.logger.error("Not correct length read for FPS")
            return
        
        def on_fps(fps):
            self.logger.debug("Sending FPS!")
            self.send(struct.pack("!Bf", cmds.FPS, fps))

        self.tracker.getRate(on_fps)

    def sayCheese(self):
        try:
            data = self.conn.recieve(lengths.OST)
        except error:
            self.panic("Error on read of ost")
            return

        if not len(data) == lengths.OST:
            self.logger.error("Not correct length read for OST")
            return
        self.send("Appenzeller")

    def IAmATeapot(self):
        self.send("418 I am a teapot!")

    def Flash_Kludge(self):
        try:
            data = self.conn.recieve(lengths.FLASH_KLUDGE)
            
        except error:
            self.panic("Error on read of flashkludge")

        self.send('<?xml version="1.0"?><cross-domain-policy><allow-access-from domain="*" to-ports="*" ></cross-domain-policy>\0')
