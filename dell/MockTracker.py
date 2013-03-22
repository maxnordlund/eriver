from multiprocessing import Process
from threading import Thread
from ETinterface import (EyeTracker, ETEvent, ETError)
import time

#Fake eye tracker that gives points in a circle.
#Thinking about making the calibration set up a polygon that is traced instead.
class MockTracker(EyeTracker):
    def __init__(self, onETEventHandler, name=1):
        self.active=True
        self.calibrating=False
        self.name=name
        self.onETEventHandler = onETEventHandler

        proc = Thread(target=self.run)
        
        proc.start()

    def enable(self, yes=True):
        self.active = yes
        return True

    def getState(self):
        return 0 + self.active + (self.calibrating << 1)

    def startCalibration(self):
        self.calibrating=True
        return True

    def endCalibration(self):
        self.calibrating=False
        return True

    def clearCalibration(self):
        return True

    def addPoint(self, x, y):
        return True

    def getName(self):
        return self.name

    def onETEvent(self, etevent):
        print("DATA!")
        self.onETEventHandler(etevent)

    def run(self):
        print("Starting generation of points!")
        for event in circle_generator(radius=0.2, offset=(0.5, 0.5)):
            #print("ETDATA!" + str(self.active))
            if self.active:
                #print("Active!")
                self.onETEvent(event)
        
            
def circle_generator(radius=1, offset=(0,0), step=0.01, start=0, stop=None):
    t=start
    while stop==None or t<stop:
        #yield ETEvent(0.5, 0.5, 0)
        yield ETEvent(math.cos(t)*radius+offset[0], y=math.sin(t)*radius+offset[1], int(time.time()*1000))
        t+=step
    
