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

class ETError(RuntimeError):


class ETEvent(object):
    __init__(self, x, y, timestamp):
        self.x=x
        self.y=y
        self.time=timestamp
    
