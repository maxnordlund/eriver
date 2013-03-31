from multiprocessing import Process
from threading import (Thread, Lock)
import time
import Queue

from ETinterface import (EyeTracker, ETEvent, ETError)

from tobii.eye_tracking_io.types import Point2D
from tobii.eye_tracking_io.basic import EyetrackerException
import tobii.eye_tracking_io.mainloop
import tobii.eye_tracking_io.browsing
import tobii.eye_tracking_io.eyetracker



from collections import namedtuple

# Tuple of x,y weights
Weights = namedtuple("Weights", ["x", "y"])

errorcodes = {
        "et_connect": 4041
    }

weights = { # These are the values we can get.
    Weights(0,0): Weights(0.5, 0.5), #(left_validity, right_validity): (left_weight, right_weight)
    Weights(4,0): Weights(0.1, 0.9),
    Weights(3,1): Weights(0.3, 0.7),
    Weights(2,2): Weights(0.5, 0.5),
    Weights(1,3): Weights(0.7, 0.3),
    Weights(0,4): Weights(0.9, 0.1),
    Weights(4,4): Weights(0, 0),
}

# Implements the interface given in documentation to EyeTracker class.
# Implementation for Tobii's range of 3.0 analytics eyetrackers
class AnalyticsTracker(EyeTracker):
    def __init__(self, onETEvent, etid=None, name=1, fps=60):
       super(AnalyticsTracker, self).__init__()
       tobii.eye_tracking_io.init()
       self.running = True
       self.queue = Queue.Queue()

       self.enabled = False
       self.calibration = False

       self.mainloop = tobii.eye_tracking_io.mainloop.MainloopThread()
       self.etid = None
       self.et = None
       self.thread = Thread(target=self.connect)
       self.thread.start()

       def marshaller():
           while self.running:
               f = self.queue.get()
               f()
       
       Thread(target=marshaller).start()
       
       

    # Set if the tracker should be active.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def enable(self,blocking, callback, *args, **kwargs):

        if not blocking and self.et == None:
            callback(False, *args, **kwargs)
            return

        while self.et == None:
            pass

        # What is a and b?
        # Who knows?
        # Tobii.. Perhaps...
        def on_start_tracking(a, b):
            self.enabled = True
            callback(True, *args, **kwargs)
            
        self.et.StartTracking(on_start_tracking)

    # Set if the tracker should be active or not.
    # This might shutdown the tracker if the implementation wants to.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def disable(self, callback, *args, **kwargs):
        if self.et == None:
            self.enqueue(callback, False, *args, **kwargs)
            return

        def on_stop_tracking(a, b):
            self.enabled = False
            callback(True, *args, **kwargs)
            
        self.et.StopTracking(on_stop_tracking)

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
        
        if self.et == None:
            print("-1")
            self.enqueue(callback, -1, *args, **kwargs)
            return

        print("WHAT?")
        if (self.enabled and self.calibrating):
            print("3")
            self.enqueue(callback, 3, *args, **kwargs)
            return
        
        if (not self.enabled) and self.calibrating:
            print("2")
            self.enqueue(callback, 2, *args, **kwargs)
            return

        if self.enabled and (not self.calibrating):
            print("1")
            self.enqueue(callback, 1, *args, **kwargs)
            return

        if (not self.enabled) and (not self.calibrating):
            print("0")
            self.enqueue(callback, 0, *args, **kwargs)
            return

        print("-2")
        self.enqueue(callback, -2, *args, **kwargs)
            

    # Puts the tracker in calibration mode.
    # The angle may be disregarded if not necessary, but it represents the angle
    # between the normal vector of the users table and the tracker.
    # If the tracker does not support calibration, return False.
    # If the tracker could not be placed in calibration mode, return False.
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def startCalibration(self, angle, callback, *args, **kwargs):
        if self.et == None:
            self.enqueue(callback, False, *args, **kwargs)
            return
        
        #self.et.StopTracking()
        self.et.StartCalibration(self, callback, True, *args, **kwargs) 

    # Takes the tracker out of calibration mode.
    # If the tracker could not be taken out of calibration mode, return False
    # callback is called with a result, *args and **kwargs when the operation is completed.
    def endCalibration(self, callback, *args, **kwargs):
        if self.et == None:
            self.enqueue(callback, False, *args, **kwargs)
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
            self.enqueue(callback, False, *args, **kwargs)
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
            self.enqueue(callback, False, *args, **kwargs)
            return
        self.et.AddCalibrationPoint((x, y), callback, True, *args, **kwargs)

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
            self.enqueue(callback, set([0]), *args, **kwargs)
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
            self.enqueue(callback, False, *args, **kwargs)
            return
        self.et.SetFramerate(rate, callback, *args, **kwargs)

    def etlooker(self, event_type, event_name, et_info):
        #I should write this soon.
        #print(event_type)
        #print(event_name)
        print("%s: %s" % (str(event_name), str(et_info)))
        if event_type == tobii.eye_tracking_io.browsing.EyetrackerBrowser.FOUND:
            
            def setTracker(error, eyetracker, eyetracker_info):
                if error:
                    if error == 0x20000402: #Magical error code
                        raise ETError(error, "The selected unit is too old, a unit which supports protocol version 1.0 is required.\n\nDetails: %s" % error)
                    else:    
                        raise ETError(errorcodes["et_connect"], "Could not connect to %s" % (eyetracker_info))
                    
                self.et = eyetracker
                self.etid = str(eyetracker_info)
                self.et.events.OnGazeDataReceived += self.henshin
                print("Tracker created!")
                     
            if (not self.etid == None) and self.etid == str(et_info):
                
                tobii.eye_tracking_io.eyetracker.Eyetracker.create_async(self.mainloop, et_info, lambda error, eyetracker: self.enqueue(setTracker, error, eyetracker, et_info))
            else:
                self.etid = str(et_info)
                tobii.eye_tracking_io.eyetracker.Eyetracker.create_async(self.mainloop, et_info, lambda error, eyetracker: self.enqueue(setTracker, error, eyetracker, et_info))
            print("FOUND Event Handled")
        
        if event_type == tobii.eye_tracking_io.browsing.EyetrackerBrowser.REMOVED:
            if str(et_info) == self.etid:
                self.et = None
            print("REMOVED Event Handled")
        
        if event_type == tobii.eye_tracking_io.browsing.EyetrackerBrowser.UPDATED:
            # I have no idea of what to do here...
            print("UPDATE Event Handled")
            

    def connect(self):
        browser = tobii.eye_tracking_io.browsing.EyetrackerBrowser(self.mainloop, self.etlooker)
        
        
        while self.running:
            pass

        browser.stop()
        self.mainloop.stop()

    def enqueue(self, callback, *args, **kwargs):
        def f():
            callback(*args, **kwargs)
            
        self.queue.put(f)

    def henshin(self, error, gdi):
        if not error == 0:
            print("Errorcode: %d" % error)
        else:
            #print("Got Data for transformation!")
            #print("Left")
            lx, ly = gdi.LeftGazePoint2D.x, gdi.LeftGazePoint2D.y
            lv = gdi.LeftValidity

            #print("Right")
            rx, ry = gdi.RightGazePoint2D.x, gdi.RightGazePoint2D.y
            rv = gdi.RightValidity

            #print("Time")  
            timestamp = gdi.Timestamp

            #print("Weights")
            lweight, rweight = weights.get((lv, rv), (0,0))

            x = lx*lweight + rx*rweight
            y = ly*lweight + ry*rweight

            etevent = ETEvent(x, y, timestamp)
            self.callETEvent(etevent)
    
