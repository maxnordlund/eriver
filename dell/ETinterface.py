class EyeTracker(object):
    def onETEvent(etevent):
        pass

    def enable(yes=True):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def startCalibration(self):
        raise NotImplementedError

    def endCalibration(self):
        raise NotImplementedError

    def clearCalibration(self):
        raise NotImplementedError

    def addPoint(self, x, y):
        raise NotImplementedError

    def getName(self):
        return "Eye Tracker"

class ETError(Exception):

    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return "ETError! Error code %d: %s" % (self.code, self.text)


class ETEvent(object):
    def __init__(self, x, y, timestamp):
        self.x=x
        self.y=y
        self.timestamp=timestamp
    
