import sys
import getopt
from game.Util.Log import LogConsole

def convertMap():
	#from tools.editor import convert
	from game.Util.editor import convert
	convert.runConvert()

if __name__ == '__main__':
	# Parse arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hmd", ["help", "convert-map", "debug"])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		print("Figure it out!")
		sys.exit(2)
	
	import __builtin__
	__builtin__.LOG = LogConsole()
	__builtin__.DEBUG = 0
	
	for o, a in opts:
		if o in ("-m", "--convert-map"):
			convertMap()
		elif o in ("-d", "--debug"):
			__builtin__.DEBUG = a
		elif o in ("-h", "--help"):
			print("Figure it out!")
			sys.exit()
		else:
			assert False, "unhandled option"