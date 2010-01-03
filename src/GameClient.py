''' GameClient.py
	
	The game client initializes all the game.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			* Make the PSGClient a singleton.
'''

# Python imports
import sys, cPickle, os

# Panda imports
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import FrameBufferProperties
from pandac.PandaModules import GraphicsPipe
from pandac.PandaModules import WindowProperties

# PSG imports
from ClientConnection import ClientConnection
#from GSEng.Game import Game
from GUI.core import Gui
from GUI.keys import Keys
from GUI.rtheme import RTheme
from GUI.mainmenu import MainScreen
from Settings import GameSettings
import Event
import GameConsts
from GSEng import GameStateMgr
#from GSEng import Player
from GXEng import GXMgr
from Util.Log import LogConsole

class GameClient(DirectObject):
	''' GameClient
	GameClient creates the Dispatcher, ClientConnection, GSM and GUI. Then it
	sits back and chills. The GUI handles setting organizing the rest of the
	setup, the dispatcher handles all communication and the GSM handles the
	game.
	'''
	def __init__(self):
		import __builtin__
		__builtin__.LOG = LogConsole()
		
		print("Starting PSG Client ...")
				
		# Initialize event dispatcher
		self._dispatcher = Event.Dispatcher()
		self._dispatcher.register(self, 'E_StartGame', self.startGame)
		self._dispatcher.register(self, 'E_ExitGame', self.exitGame)
		self._dispatcher.register(self, 'E_ExitProgram', self.exitProgram)
		
		# Create server connection object
		self.clientconnection = ClientConnection()

		# Load settings
		self.gst = GameSettings()
		self.gst.loadSettings()
		
		# Create map store which holds and manipulates our available maps
		#self.mstore = Map.MapStore()
		#print(self.mstore.availableMaps)
		
		# Start menu GUI
		self.gui = Gui(Keys(),theme=RTheme())
		self.menu = MainScreen(self)
		
		# These will be initialized upon starting the actual game
		#self.viewstate          = None
		#self.gamestatemgr       = None
		#self.keyboardcontroller = None
		#self.mousecontroller    = None
		#self.gameFrame          = None
		
		#self.reloadMaps()
		#self.reloadPlayers()
		
		# Pollute the global namespace
		##import __builtin__
		##__builtin__.gcli = self
		# Create GUI system
		##
		
		# Show the main menu which will call start game
		##self.menu = MainScreen()
		
			
	#def reloadPlayers(self):
	#	''' Reload the list of available players.'''
	#	self.availablePlayers = {}
	#	for playerFile in Player.getPlayerFiles():
	#		fh = open(Player.PLAYER_PATH + playerFile, 'rb')
	#		player = cPickle.load(fh)
	#		self.availablePlayers[playerFile] = player.name
		
	#def createGame(self):
	#	''' If we are playing a single player game or hosting a multiplayer game
	#		we must first create the game.'''
	#	if (self._gameType == 'Multiplayer'):
	#		# Create the game and submit it to the server
	#		print('Creating a multiplayer game')
	#	elif (self._gameType == 'Singleplayer'):
	#		print('Creating a singleplayer game')
			
	#def loadGame(self, file):
	#	'''Load a saved game from a file'''
	#	pass
		
	def startGame(self, event):
		# Kill current screen
		del(self.menu)
		del(self.gui)
		
		# Create GSM
		self.gamestate = GameStateMgr.GameStateManager()
		
		# Setup controls
		self.keyboardcontroller = Controller.KeyboardController()
		self.mousecontroller = Controller.MouseController()
		
		# Create GXEng
		
		#self.viewstate = ViewStateMgr.ViewStateManager()
		#self.viewstate.addView(View.GameView())
		#self.viewstate.addView(View.ConsoleView())
		
		self.gamestate.newGame(self.curr_game)
		#self.gamestate.loadGame(self.curr_game)
		#self.gameFrame = GameWindow()
		self.gamestate.startGame()
		
	def exitGame(self, event):
		''' Clean up open/running game. Show mainmenu.'''
		pass
		
	def exitProgram(self, event):
		# do any necessary cleanup
		if self.clientconnection.isConnected():
			self.clientconnection.disconnect(None)
		sys.exit(0)
		