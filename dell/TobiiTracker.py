from multiprocessing import Process
from threading import (Thread, Lock)
import time
import Queue

from ETinterface import (EyeTracker, ETEvent, ETError)

from tobii import eye_tracking_io as etio
from etio import (browsing, mainloop, )

# Implements the interface given in documentation to EyeTracker class.
# Implementation for Tobii's range of 3.0 analytics eyetrackers
class AnalyticsTracker(EyeTracker):
    def __init__(self, onETEvent, name=1, fps=60):
       etio.init()
       self.running = True
       self.queue = Queue.Queue()

       self.mainloop = etio.mainloop.MainloopThread()
       
       self.thread = Thread(target=self.connect)
       self.thread.start()

       def marshaller():
           for job in self.queue:
               job()
       
       Thread(target=marshaller).start()
       

    # Set if the tracker should be active.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def enable(self, callback, *args, **kwargs):
        weight = { # These are the values we can get.
            (0,0): (0.5, 0.5) #(left_validity, right_validity): (left_weight, right_weight)
            (4,0): (0.1, 0.9)
            (3,1): (0.3, 0.7)
            (2,2): (0.5, 0.5)
            (1,3): (0.7, 0.3)
            (0,4): (0.9, 0.1)
            (4,4): (0, 0)
            }
        def henshin(gdi):
            lx, ly, lv = gdi.LeftGazePoint2D, gdi.LeftValidity
            rx, ry, lv = gdi.RightGazePoint2D, gdi.LeftValidity
            timestamp = gdi.Timestamp

            lweight, rweight = weights.get((lv, rv), (0,0))

            x = lx*lweight + rx*rweight
            y = lxy*lweight + ry*rweight

            etevent = ETEvent(x, y, timestamp)
            self.callETEvent(etevent)
            
        self.et.StartTracking(henshin)
        callback(True, *args, **kwargs)

    # Set if the tracker should be active or not.
    # This might shutdown the tracker if the implementation wants to.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def disable(self, callback, *args, **kwargs):
        self.et.StopTracking(callback, *args, **kwargs)

    # Allows callers to query the tracker for a statuscode.
    # Specific to implementations but some codes should be respected
    # 0: Not enabled and not calibrating
    # 1: Enabled and not calibrating
    # 2: Calibrating but not enabled
    # 3: Enabled and calibrating
    #
    # Other than that, implementations may do what ever they feel fitting.
    # callback is called with the status, *args and **kwargs.
    def getState(self, callback, *args, **kwargs):
        raise NotImplementedError

    # Puts the tracker in calibration mode.
    # The angle may be disregarded if not necessary, but it represents the angle
    # between the normal vector of the users table and the tracker.
    # If the tracker does not support calibration, return False.
    # If the tracker could not be placed in calibration mode, return False.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def startCalibration(self, angle, callback, *args, **kwargs):
        if self.et == None:
            callback(False, *args, **kwargs)
            return
        
        #self.et.StopTracking()
        self.et.StartCalibration(self, callback, True, *args, **kwargs) 

    # Takes the tracker out of calibration mode.
    # If the tracker could not be taken out of calibration mode, return False
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def endCalibration(self, callback, *args, **kwargs):
        if self.et == None:
            callback(False, *args, **kwargs)
            return

        def onComputationCompleted():
            self.enqueue(self.et.StopCalibration,callback, True, *args, **kwargs)

        self.et.ComputeCalibration(onComputationCompleted)

    # Clears any calibration actions done.
    # Restore the tracker to a state equal to that
    # right after calibration was initiated.
    # callback is called with *args and **kwargs when the operation is completed.
    def clearCalibration(self, callback, *args, **kwargs):
        if self.et == None:
            callback(False, *args, **kwargs)
            return
        self.et.ClearCalibration(callback, True, *args, **kwargs)

    # Adds the point (x, y) to the calibration.
    # When this is called, the user is expected to be looking at that point.
    # callback is called with result, *args and **kwargs when the operation is completed.
    # result is False if the point could not be added.
    # result is False if the tracker is not calibrating.
    # Otherwise, result is True.
    def addPoint(self, x, y, callback, *args, **kwargs):
        if self.et == None or not self.calibrating:
            callback(False, *args, **kwargs)
            return
        self.et.AddCalibrationPoint(self, (x, y), callback=None, True, *args, **kwargs)

    # Free for interpretation of the implementor.
    # callback is called with name, *args and **kwargs when the operation is completed.
    def getName(self, callback, *args, **kwargs):
        callback(0, *args, **kwargs)

    # Gives a set of rates for which the tracker supports delivery of ETEvent.
    # Common values include 24, 25 30, 60 and 120.
    # Use -1 for unknown or variable rates.
    # If -1 is returned, the implementation takes it upon itself to be able to handle all requested framerates.
    # callback is called with rates, *args and **kwargs when the operation is completed.
    def getRates(self, callback, *args, **kwargs):
        if self.et == None:
            callback(set([0]), *args, **kwargs)
            return
        self.et.EnumerateFramerates(callback, *args, **kwargs)

    def getRate(self, callback, *args, **kwargs):
        callback(0, *args, **kwargs)

    # Sets the tracker rate to the given value.
    # The value given should be among those returned from getRates, excluding -1.
    # callback is called with result, *args and **kwargs when the operation is completed.
    # result is the rate that is set.
    def setRate(self, rate, callback, *args, **kwargs):
        if self.et == None:
            callback(False, *args, **kwargs)
            return
        self.et.SetFramerate(rate, callback, *args, **kwargs)

    def etlooker(self):
        

    def connect(self):
        browser = etio.browsing.EyetrackerBrowser(self.mainloop, etlooker)
        
        while self.running:
            pass

        browser.stop()
        self.mainloop.stop()

    def enqueue(self, callback, *args, **kwargs):
        def f():
            callback(*args, **kwargs)
            
        self.queue.put(f)
    
