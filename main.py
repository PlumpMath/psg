from pandac.PandaModules import loadPrcFileData
#from pandac.PandaModules import loadPrcFile 
#loadPrcFile("data/Config.prc")
#loadPrcFileData("", "want-directtools #t")
#loadPrcFileData("", "want-tk #t")
#loadPrcFileData('', 'sync-video 0')
#loadPrcFileData('', 'want-pstats 1')
loadPrcFileData('', 'win-size 640 480')
loadPrcFileData('', 'win-origin 520 285')
loadPrcFileData('', 'window-title PSG')
loadPrcFileData('', 'undecorated 1')
loadPrcFileData("", "model-path ./data/models")
loadPrcFileData("", "model-path ./data/themes")
loadPrcFileData("", "texture-path ./data/textures")
loadPrcFileData("", "sound-path ./data/sfx")
#loadPrcFileData("", "particle-path ./data/gfx")

import direct.directbase.DirectStart
from pandac.PandaModules import PStatClient
import sys

if __name__ == '__main__':
	# Add the code directory to path and import what we need
	sys.path.append('./src')
	import GameClient
	#import GameServer
	
	#serverInstance = GameServer.GameServer()
	clientInstance = GameClient.GameClient()
	#PStatClient.connect()
	run()
