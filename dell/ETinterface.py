# A default implementation of onETEvent
def default_onETEvent(etevent):
    pass

class EyeTracker(object):

    # A variable holding a function.
    # It is called when a point is gotten from the tracker.
    onETEvent = default_onETEvent

    # This method calls the function variable onETEvent.
    # As the parameter it use the second parameter.
    # That should be of the type ETEvent or similar.
    # Can be overrided if the data should be manipulated before client use
    # or if extra side effects should be performed.
    def callETEvent(self, etevent):
        self.onETEvent(etevent)

    # Set if the tracker should be active or not.
    # This might shutdown the tracker if the implementation wants to.
    def enable(yes=True):
        raise NotImplementedError

    # Allows callers to query the tracker for a statuscode.
    # Specific to implementations but some codes should be respected
    # 0: Not enabled and not calibrating
    # 1: Enabled and not calibrating
    # 2: Calibrating but not enabled
    # 3: Enabled and calibrating
    #
    # Other than that, implementations may do what ever they feel fitting.
    def getState(self):
        raise NotImplementedError

    # Puts the tracker in calibration mode.
    # The angle may be disregarded if not necessary, but it represents the angle
    # between the normal vector of the users table and the tracker.
    # If the tracker does not support calibration, return False.
    # If the tracker could not be placed in calibration mode, return False.
    def startCalibration(self, angle):
        raise NotImplementedError

    # Takes the tracker out of calibration mode.
    # If the tracker could not be taken out of calibration mode, return False
    def endCalibration(self):
        raise NotImplementedError

    # Clears any calibration actions done.
    # Restore the tracker to a state equal to that
    # right after calibration was initiated.
    def clearCalibration(self):
        raise NotImplementedError

    # Adds the point (x, y) to the calibration.
    # When this is called, the user is expected to be looking at that point.
    # Returns False if the point could not be added.
    # Returns False if the tracker is not calibrating.
    # Otherwise, return True.
    def addPoint(self, x, y):
        raise NotImplementedError

    # Free for interpretation of the implementor.
    # Returns a integer that identifies the tracker.
    def getName(self):
        return 0

    # Gives a set of rates for which the tracker supports delivery of ETEvent.
    # Common values include 24, 25 30, 60 and 120.
    # Use -1 for unknown or variable rates.
    # If -1 is returned, the implementation takes it upon itself to be able to handle all requested framerates.
    def getRates(self):
        return set([-1])

    # Sets the tracker rate to the given value.
    # The value given should be among those returned from getRates, excluding -1.
    # Returns True if the rate is set to the value. Otherwise it returns False.
    def setRate(self, rate):
        raise NotImplementedError

# Error raised if something is wrong with a tracker.
# An error code and explaining text can be attached.
class ETError(Exception):

    def __init__(self, code=0, text=""):
        self.code = code
        self.text = text

    def __str__(self):
        return "ETError! Error code %d: %s" % (self.code, self.text)

# Class holding data of a single eye tracking event.
# Data avaliable is x and y coordinates and a timestamp of the event. 
class ETEvent(object):
    def __init__(self, x, y, timestamp):
        self.x=x
        self.y=y
        self.timestamp=timestamp
    
