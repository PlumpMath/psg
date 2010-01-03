# Python imports
import sys
import getopt

# Panda imports
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-type none")
loadPrcFileData('', 'client-sleep 0.01')
import direct.directbase.DirectStart

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
	for o, a in opts:
		if o in ("-d", "--debug"):
			DEBUG = a
		elif o in ("-h", "--help"):
			print("Figure it out!")
			sys.exit()
		else:
			assert False, "unhandled option"
	
	# Add the code directory to path and import what we need
	sys.path.append('./src')
	from Server.GameServer import PSGServer
	
	# Run the server
	server = PSGServer()
	run()