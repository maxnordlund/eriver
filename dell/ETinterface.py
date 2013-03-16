class EyeTracker(object):
    def onETEvent(etevent):
        pass

    def enable(yes=True):
        raise NotImplementedError

    def getState():
        raise NotImplementedError


class ETError(RuntimeError):


class ETEvent(object):
    __init__(self, x, y, timestamp):
        self.x=x
        self.y=y
        self.time=timestamp
    
