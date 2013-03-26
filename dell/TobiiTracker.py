from multiprocessing import Process
from threading import Thread
from ETinterface import (EyeTracker, ETEvent, ETError)
import time
from tobii import eye_tracking_io as etio
from etio import (browsing, mainloop, )

# Implements the interface given in documentation to EyeTracker class.
#Fake eye tracker that gives points in a circle.
#Thinking about making the calibration set up a polygon that is traced instead.
class MockTracker(EyeTracker):
    def __init__(self, onETEvent, name=1, fps=60):
       etio.init()
       self.running = True

       self.mainloop = etio.mainloop.MainloopThread()
       
       self.thread = Thread(target=self.run)
       self.thread.start()       

    def enable(self, yes=True):
        pass

    def getState(self):
        pass

    def startCalibration(self, angle):
        return False

    def endCalibration(self):
        return False

    def clearCalibration(self):
        return False

    def addPoint(self, x, y):
        return False

    def getName(self):
        return 0

    def getRates(self):
        return set([0])

    def getRate(self):
        et.etFramerate()
        
    def setRate(self, rate):
        pass

    def etlooker(self):
        

    def run(self):
        browser = etio.browsing.EyetrackerBrowser(self.mainloop, self.etlooker)
        while self.running:
            
            
        self.mainloop.stop()
            
    
