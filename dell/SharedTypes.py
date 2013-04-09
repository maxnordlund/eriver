class Command(object):
	def __init__(self, cmd, args, callback):
		self.cmd = cmd
		self.args = args
		self.callback = callback