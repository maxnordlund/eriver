class EyeTracker(object):
    def onETEvent(etevent):
        pass

    def enable(yes=True):
        raise NotImplementedError

    def getState():
        raise NotImplementedError

    def startCalibration():
        raise NotImplementedError

    def endCalibration():
        raise NotImplementedError

    def clearCalibration():
        raise NotImplementedError

    def addPoint(x, y):
        raise NotImplementedError

class ETError(RuntimeError):


class ETEvent(object):
    __init__(self, x, y, timestamp):
        self.x=x
        self.y=y
        self.time=timestamp
    
