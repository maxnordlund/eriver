from multiprocessing import Process
from threading import Thread
from ETinterface import (EyeTracker, ETEvent, ETError)
import time
import math

# Implements the interface given in documentation to EyeTracker class.
#Fake eye tracker that gives points in a circle.
#Thinking about making the calibration set up a polygon that is traced instead.
class MockTracker(EyeTracker):
    def __init__(self, onETEvent, name=1, fps=60):
        super(MockTracker, self).__init__()
        self.active=False
        self.calibrating=False
        self.name=name
        self.register_onETEvent(onETEvent)
        self.fps = fps
        
        proc = Thread(target=self.run)
        
        proc.start()

    def enable(self, callback, *args, **kwargs):
        self.active = True
        callback(True, *args, **kwargs)

    def disable(self, callback, *args, **kwargs):
        self.active = False
        callback(True, *args, **kwargs)

    def getState(self, callback, *args, **kwargs):
        status = 0 + self.active + (self.calibrating << 1)
        callback(status, *args, **kwargs)

    def startCalibration(self, angle, callback, *args, **kwargs):
        self.calibrating=True
        callback(True, *args, **kwargs) # Does not really support it, but fakes it.

    def endCalibration(self, callback, *args, **kwargs):
        self.calibrating=False
        callback(True, *args, **kwargs)

    def clearCalibration(self, callback, *args, **kwargs):
        callback(True, *args, **kwargs)

    def addPoint(self, x, y, callback, *args, **kwargs):
        callback(True, *args, **kwargs)

    def getName(self, callback, *args, **kwargs):
        callback(self.name, *args, **kwargs)

    def getRates(self, callback, *args, **kwargs):
        rates = set([24, 25, 30, 60, 120])
        callback(rates, *args, **kwargs)

    def getRate(self, callback, *args, **kwargs):
        callback(fps, *args, **kwargs)

    def setRate(self, rate, callback, *args, **kwargs):
        self.fps = rate
        self.getRate(callback, *args, **kwargs)

    def circle_generator(self, radius=1, offset=(0,0), step=0.01, start=0, stop=None):
        t=start
        while stop==None or t<stop:
            #yield ETEvent(0.5, 0.5, 0)
            yield ETEvent(x=math.cos(t)*radius+offset[0], y=math.sin(t)*radius+offset[1], timestamp=int(time.time()*1000))
            t+=step

    def run(self):
        print("Starting generation of points!")
        for event in self.circle_generator(radius=0.2, offset=(0.5, 0.5)):
            #print("ETDATA!" + str(self.active))
            if self.active:
                #print("Active!")
                self.callETEvent(event)
            time.sleep(1.0/self.fps)
