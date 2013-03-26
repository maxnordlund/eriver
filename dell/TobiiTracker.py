from multiprocessing import Process
from threading import (Thread, Lock)
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
        lock = threading.Lock()

        #Does this work? YES IT DOES!
        def start_calibrator(event_type, event_name, eyetracker_info):
            lock.release()
        
        lock.acquire() #asynchronous to synchronous
        browser = self.et.StartCalibration(self, callback=startcalibrator)
        lock.acquire()

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
        

    def run(self):

        lock = threading.Lock()

        #Does this work? YES IT DOES!
        def etlooker(event_type, event_name, eyetracker_info):
            if event_type == etio.EyetrackerBrowser.FOUND:
                if eyetracker_info.status == "ok"
                    self.et = 
                    lock.release()
                
            elif event_type == etio.EyetrackerBrowser.UPDATED:
                pass
            elif event_type == etio.EyetrackerBrowser.REMOVED:
                pass
            
        
        lock.acquire() #asynchronous to synchronous
        browser = etio.browsing.EyetrackerBrowser(self.mainloop, etlooker)
        lock.acquire()
        lock.release()
        while self.running:
            pass

        browser.stop()
        self.mainloop.stop()
            
    
