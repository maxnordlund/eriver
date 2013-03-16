from multiprocessing import Process

#Fake eye tracker that gives points in a circle.
#Thinking about making the calibration set up a polygon that is traced instead.
class MockTracker(EyeTracker, Process):
    def __init__(self, name="MockTracker"):
        self.active=False
        self.calibrating=False
        self.name=name
        self.start()

    def enable(self, yes=True):
        self.active = yes

    def getState(self):
        return 0 + self.active + (self.calibrating << 1)

    def startCalibration(self):
        self.calibrating=True

    def endCalibration(self):
        self.calibrating=False

    def clearCalibration(self):
        pass

    def addPoint(self, x, y):
        pass

    def getName(self):
        return self.name
        

    def run(self):
        for event in circle_generator(radius=0.2, offset=(0.5, 0.5)):
            if self.sendEvent:
                self.onETEvent(event)
            else:
                return
        
            
def circle_generator(radius=1, offset=(0,0), step=0.01, start=0, stop=None):
    t=start
    while stop==None or t<stop:
        yield ETEvent(math.cos(t)*radius+offset[0], y=math.sin(t)*radius+offset[1], int(time.time()*1000))
        t+=step
        
    
