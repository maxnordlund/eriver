from multiprocessing import Process
from threading import (Thread, Lock)
from ETinterface import (EyeTracker, ETEvent, ETError)
import time
from tobii import eye_tracking_io as etio
from etio import (browsing, mainloop, )

# Implements the interface given in documentation to EyeTracker class.
# Implementation for Tobii's range of 3.0 analytics eyetrackers
class AnalyticsTracker(EyeTracker):
    def __init__(self, onETEvent, name=1, fps=60):
       etio.init()
       self.running = True

       self.mainloop = etio.mainloop.MainloopThread()
       
       self.thread = Thread(target=self.run)
       self.thread.start()       

    # Set if the tracker should be active.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def enable(self, callback, *args, **kwargs):
        raise NotImplementedError

    # Set if the tracker should be active or not.
    # This might shutdown the tracker if the implementation wants to.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def disable(self, callback, *args, **kwargs):
        raise NotImplementedError

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
        raise NotImplementedError

    # Takes the tracker out of calibration mode.
    # If the tracker could not be taken out of calibration mode, return False
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def endCalibration(self, callback, *args, **kwargs):
        raise NotImplementedError

    # Clears any calibration actions done.
    # Restore the tracker to a state equal to that
    # right after calibration was initiated.
    # callback is called with *args and **kwargs when the operation is completed.
    def clearCalibration(self, callback, *args, **kwargs):
        raise NotImplementedError

    # Adds the point (x, y) to the calibration.
    # When this is called, the user is expected to be looking at that point.
    # callback is called with result, *args and **kwargs when the operation is completed.
    # result is False if the point could not be added.
    # result is False if the tracker is not calibrating.
    # Otherwise, result is True.
    def addPoint(self, x, y, callback, *args, **kwargs):
        raise NotImplementedError

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
        callback(set([-1]), *args, **kwargs)

    def getRate(self, callback, *args, **kwargs):
        callback(0, *args, **kwargs)

    # Sets the tracker rate to the given value.
    # The value given should be among those returned from getRates, excluding -1.
    # callback is called with result, *args and **kwargs when the operation is completed.
    # result is the rate that is set.
    def setRate(self, rate, callback, *args, **kwargs):
        raise NotImplementedError

    def run(self):

        lock = threading.Lock()

        #Does this work? YES IT DOES!
        def etlooker(event_type, event_name, eyetracker_info):
            pass
        
        lock.acquire() #asynchronous to synchronous
        browser = etio.browsing.EyetrackerBrowser(self.mainloop, etlooker)
        lock.acquire()
        lock.release()
        
        while self.running:
            pass

        browser.stop()
        self.mainloop.stop()
    
