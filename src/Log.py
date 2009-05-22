import Event

class LogConsole():
	"""A class that listens for events and prints them out
	to the console"""
	def __init__(self):
		print("LOG")
		Event.Dispatcher().register(self, 'E_All', self.printEvents)
		
	def printEvents(self, event):
		print("==CONSOLE: Event Log==========================================")
		print(str(event))
		#print("========================================================")


def printFBProps():
	print("FRAMEBUFF PROPS--------------------------------")
	print("accumbits " + str(fbProps.getAccumBits()))
	print("multisamples " + str(fbProps.getMultisamples()))
	print("alphabits " + str(fbProps.getMultisamples()))
	print("accumbits " + str(fbProps.getAccumBits()))
	print("colorbits " + str(fbProps.getColorBits()))
	print("depthbits " + str(fbProps.getDepthBits()))
	print("indexedcolor " + str(fbProps.getIndexedColor()))
	print("rgbcolor " + str(fbProps.getRgbColor()))
	print("stencilbits " + str(fbProps.getStencilBits()))
