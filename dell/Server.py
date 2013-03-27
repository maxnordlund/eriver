from network import TCPHandler
from socket import error
import logging
from threading import (Thread, Lock)
from multiprocessing import (Process, Queue)

from ConnHandler import ConnHandler
from MockTracker import MockTracker
from TobiiTracker import AnalyticsTracker as TobiiTracker

import struct
import datetime

LOG_FILENAME = 'eriver.log'
FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

def enum(**enums):
	return type('Enum', (), enums)

tracker_types = enum(MOCK="MOCK", TOBII="TOBII")

class ETServer(object):
    def __init__(self, addr, tracker, name="ETServer"):
        self.shutdown = False # A way for any part of the server to give a shutdown signal
        
        self.handlers = dict()# All the handlers of the server
        self.handlersLock = Lock()# A lock to regulate when parts can use the handlers.
        
        self.eyetracker = tracker #We need a tracker aswell.
        self.eyetracker.register_onETEvent(self.sendData)
        
        self.logger = logging.getLogger(name) # A logger is good to have
        
        self.serverSocket = TCPHandler(addr, None, True) # Create a server socket for listening to connection attempts

    def sendData(self, etevent):
        for h in self.handlers.keys():
            (proc, events) = self.handlers[h]
            if proc.is_alive():
                #self.logger.debug(str(h) + str(h.listen))
                events.put(etevent, False) #Do not block. Either the reciver is ready, or not. Can't wait.
            else:
                del self.handlers[h]
                

    def start(self):
        lock = Lock() # For syncronization

        def on_enable(res):
            if not res:
                self.logger.critical("WAT? Eye tracker not enablable?")
                self.shutdown = True
            lock.release()

        lock.acquire()
        self.eyetracker.enable(blocking=True, callback=on_enable)

        lock.acquire()
                
        def on_status(res):
            self.logger.debug("Status? %d" % res)

        self.eyetracker.getState(on_status)
        
        def QueueWorker(eyetracker, queue):
            while 1:
                command = queue.get()
                eyetracker.__getattribute__(command.cmd)(*command.args, callback=callback)
        
        with self.serverSocket: # Start listen and make sure it is closed!
            cmds = Queue()
            while not self.shutdown: #Loop until we recive signal of shutdown
                try:
                    conn, addr = self.serverSocket.accept() #Blockingly accept connections
                    self.logger.info("\t\t\tFRIEND! AWSUM THX!")
                    events = Queue()
                    h = ConnHandler(conn, addr, events, cmds) #Take new connection and fork off a handler
                    proc = Process(target=h.start(), daemon=True).start() #And kick it away!
                    self.handlers[h] = (proc, events)
                except (error, KeyboardInterrupt) as e:
                    self.shutdown = True #O NOES!
                    for h in self.handlers:
                        h.join() #CAN I HAS SYNCZ?

                    if isinstance(e, error):
                        self.logger.critical("Unhandled network error in listener.")
                        raise
                    else:
                        self.logger.warning("Server stopped by user.")
                

        self.logger.info("\tPLZ CLOSE EVERYTHING!")

if __name__ == "__main__":

	from optparse import OptionParser
	import sys, traceback

	parser = OptionParser()
	parser.set_usage("python server.py [options] type=[MOCK, TOBII]")
	parser.add_option("-n", "--name", type="int", default=1,
					help="The name the server. Is sent to clients on connect.")
	parser.add_option("-l", "--loglevel", default="WARNING",
					help="Change the loglevel of the output. Default=WARNING")
	parser.add_option("-a", "--address", default="localhost",
					help="The address the server should listen on. Default='localhost'")
	parser.add_option("-p", "--port", type="int", default=3031,
					help="The port the server should listen on. Default='3031'")

	(options, args) = parser.parse_args()

	# assuming loglevel is bound to the string value obtained from the
	# command line argument. Convert to upper case to allow the user to
	# specify --log=DEBUG or --log=debug
	# Shamefullt stolen from http://docs.python.org/3.4/howto/logging.html
	numeric_level = getattr(logging, options.loglevel.upper(), None)
	if not isinstance(numeric_level, int):
		raise ValueError('Invalid log level: %s' % loglevel)

	logging.basicConfig(filemode='w', filename=LOG_FILENAME,level=numeric_level, format=FORMAT)
	
	addr = (options.address, options.port)
	logging.info("HAI")
	logging.info("CAN I HAS NETWORK?")
	logging.info("PLZ LISTEN 2 TCP " + str(addr) + "?")
	logging.info("\tAWSUM THX")
	logging.info("\t\tDO_STUFFS!")

	tracker = None
	if len(args) < 1:
		raise ValueError('No tracker type specified.')

	tracker_type = args[0].upper()
	if tracker_type == tracker_types.MOCK:
		tracker = MockTracker(name=options.name)
	elif tracker_type == tracker_types.TOBII:
		tracker = TobiiTracker(name=options.name, logger=logging.Logger("TobiiTracker"))
	else:
		raise ValueError('Invalid tracker type.\n See the help text for more information.')
	
	try:
		ETServer(addr, tracker).start()

	except Exception as e:
		logging.exception(e)
		
	finally:
		print("Stopped.")
		logging.info("KTHXBYE!")

