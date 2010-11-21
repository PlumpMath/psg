# Settings
#
# These must be set before importing DirectStart
# 
# These should be incorporated into the Settings module. We would then need to
# instantiate the settings singleton here in main before run().
from pandac.PandaModules import loadPrcFileData
#from pandac.PandaModules import loadPrcFile 
# MENU SCREEN SETTINGS
loadPrcFileData("", "win-size 640 512")
loadPrcFileData("", "win-origin 520 285")
loadPrcFileData("", "window-title PSG")
#loadPrcFileData("", "undecorated 1")
#
## PATHS
loadPrcFileData("", "model-cache-dir ./tmp/")
loadPrcFileData("", "model-path ./data/models")
loadPrcFileData("", "model-path ./data/themes")
loadPrcFileData("", "model-path ./data/textures") # This doesn't work. Why?
loadPrcFileData("", "model-path ./data/shaders")
loadPrcFileData("", "texture-path ./data/textures")
loadPrcFileData("", "sound-path ./data/sfx")
loadPrcFileData("", "particle-path ./data/gfx")
#
## DEBUG OPTIONS
#loadPrcFileData("", "show-frame-rate-meter 1")
##loadPrcFileData("", "want-pstats 1")
##loadPrcFileData("", "task-timer-verbose 1")
##loadPrcFileData("", "pstats-tasks 1")
##loadPrcFileData("", "track-memory-usage 1")
##loadPrcFileData("", "notify-level-glgsg spam")
#
## OTHER OPTIONS
loadPrcFileData("", "sync-video 0")
#loadPrcFileData("", "aspect-ratio 2.0")
#loadPrcFileData("", "notify-level fatal")
##loadPrcFileData("", "compressed-textures 1")
loadPrcFileData("", "text-pixels-per-unit 90")
loadPrcFileData("", "text-point-size 9")
loadPrcFileData("", "text-texture-margin 5")
loadPrcFileData("", "geom-cache-size 300")
#loadPrcFileData("", "pstats-tasks 1")
#loadPrcFileData("", "pstats-tasks 1")
#loadPrcFileData("", "window-type none")
loadPrcFileData('', 'client-sleep 0.01')

# Python imports
import getopt
import sys

# Panda imports
import direct.directbase.DirectStart

# PSG imports
from game import GameClient

# Setup default globals
import __builtin__
__builtin__.DEBUG = 4
__builtin__.NOGRAPHICS = True
__builtin__.NOSERVER = True
__builtin__.NOMENU = True
__builtin__.PSTAT = False

def main():
	# Create the game instance
	gcli = GameClient.GameClient()
	
	if PSTAT:
		from pandac.PandaModules import PStatClient
		PStatClient.connect()
	
	run()

if __name__ == '__main__':
	# Add the code directory to path and import what we need
	
	# Parse arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hspd:", ["help", "noserver", "pstat", "debug="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		print("Figure it out!")
		sys.exit(2)
	
	for o, a in opts:
		if o in ("-d", "--debug"):
			__builtin__.DEBUG = a
		elif o in ("-s", "--server"):
			__builtin__.NOSERVER = True
		elif o in ("-p", "--pstat"):
			__builtin__.PSTAT = True
			sys.exit()
		elif o in ("-h", "--help"):
			print("Figure it out!")
			sys.exit()
		else:
			assert False, "unhandled option"
	
	main()
	