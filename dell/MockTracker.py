from multiprocessing import Process, Pipe

class MockTracker(EyeTracker, Process):
    def __init__(self):
        self.sendEvent=False
        self.start()

    def enable(yes=True):
        self.sendEvent=yes

    def getState():
        return 1

    def run():
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
        
    
