import direct.directbase.DirectStart
from pandac.PandaModules import loadPrcFileData
from pandac.PandaModules import loadPrcFile 
loadPrcFile("cfg/p3d.config")

# Python imports
import sys
import getopt

if __name__ == '__main__':
	# Parse arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hd:", ["help", "debug="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		print("Figure it out!")
		sys.exit(2)
	
	import __builtin__
	__builtin__.DEBUG = 0
	__builtin__.NOGRAPHICS = True
	for o, a in opts:
		if o in ("-d", "--debug"):
			__builtin__.DEBUG = a
		elif o in ("-h", "--help"):
			print("Figure it out!")
			sys.exit()
		else:
			assert False, "unhandled option"
	
	# Add the code directory to path and import what we need
	sys.path.append('./src')
	# Create the game instance
	# Panda imports
	from pandac.PandaModules import PStatClient
	import GameClient
	gcli = GameClient.GameClient()
	#PStatClient.connect()
	run()