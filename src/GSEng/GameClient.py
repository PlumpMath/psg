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
#from data.themes.psgtheme import PSGTheme
from ClientConnection import ClientConnection
from Game import ClientGame
from gui.core import GUI
from gui.keys import Keys
from gui.psgtheme import PSGTheme
from gui.mainmenu import MainScreen
from Settings import GameSettings
import Controller
import Event
import GameStateMgr
import Map
import Player
import View
import ViewStateMgr

class GameClient(DirectObject):
	''' GameClient
	GameClient creates the Dispatcher, ClientConnection, GSM and GUI. Then it
	sits back and chills. The GUI handles setting organizing the rest of the
	setup, the dispatcher handles all communication and the GSM handles the
	game.
	'''
	def __init__(self):
		print("Starting PSG Client ...")
		
		# Initialize event dispatcher
		self._dispatcher = Event.Dispatcher()
		self._dispatcher.register(self, 'E_ExitGame', self.exitGame)
		self._dispatcher.register(self, 'E_ExitProgram', self.exitProgram)

		
		
		#self.availableMaps      = {} # {filename: mapname}
		#self.availablePlayers   = {} # {filename: playername}
		
		self.clientconnection   = ClientConnection()
		self.curr_game          = ClientGame()
		# These will be initialized upon starting the actual game
		#self.viewstate          = None
		#self.gamestatemgr       = None
		#self.keyboardcontroller = None
		#self.mousecontroller    = None
		#self.gameFrame          = None
				
		# Load settings
		self.gst = GameSettings()
		self.gst.loadSettings()
		#self.reloadMaps()
		#self.reloadPlayers()
		
		# Pollute the global namespace
		import __builtin__
		__builtin__.gcli = self
		# Create GUI system
		self.gui = GUI(Keys(),theme=PSGTheme())
		
		# Show the main menu which will call start game
		self.menu = MainScreen()
		
	def reloadMaps(self):
		''' Reload the list of available maps.'''
		self.availableMaps = {}
		for mapFile in Map.getMapFiles():
			fh = open(Map.MAP_PATH + mapFile, 'rb')
			map = cPickle.load(fh)
			self.availableMaps[mapFile] = map.name
			
	def reloadPlayers(self):
		''' Reload the list of available players.'''
		self.availablePlayers = {}
		for playerFile in Player.getPlayerFiles():
			fh = open(Player.PLAYER_PATH + playerFile, 'rb')
			player = cPickle.load(fh)
			self.availablePlayers[playerFile] = player.name
		
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
		
	def makeGameEngine(self):
		''' Creates a new game engine based on settings in GameSettings.
			Information for this came from here
			http://panda3d.org/phpbb2/viewtopic.php?t=2848'''
		
		# Create a new FrameBufferProperties object using our settings
		fbProps = FrameBufferProperties()
		fbProps.addProperties(FrameBufferProperties.getDefault())
		fbProps.setMultisamples(gcli.gst.antiAlias)
		fbProps.setAlphaBits(gcli.gst.alphaBits)
		fbProps.setDepthBits(gcli.gst.colorDepth)
		
		# Create a WindowProperties object
		winProps = WindowProperties( base.win.getProperties() )
		winProps.setFullscreen(gcli.gst.fullscreen)
		winProps.setUndecorated(gcli.gst.fullscreen)
		winProps.setSize(gcli.gst.xRes,gcli.gst.yRes)
		winProps.setTitle('PSG - Project Space Game: Alpha')

		# Create the engine
		base.graphicsEngine.makeOutput(base.pipe,  # GraphicsPipe
								'mainGameOutput',  # Name
								0,                 # Sort
								fbProps,           # FrameBufferProperties
								winProps,          # WindowProperties
								GraphicsPipe.BFRequireWindow, # Flags
								base.win.getGsg()) # GraphicsStateGaurdian
		base.openMainWindow(props=winProps, gsg=base.win.getGsg(), keepCamera=1) 
		
		# Set camera properties
		base.camLens.setFov(60.0)
			
	def startGame(self):
		# Kill current screen
		del(self.menu)
		del(self.gui)
		
		print self.curr_game
		
		# Some of this will be moved to createGame / loadGame
		self.makeGameEngine()
		base.setFrameRateMeter(gcli.gst.showFPS)
		
		#print('  In GameClient - map = %s'%game.mapFileName)
		
		self.viewstate = ViewStateMgr.ViewStateManager()
		self.viewstate.addView(View.GameView())
		#self.viewstate.addView(View.ConsoleView())
		self.gamestate = GameStateMgr.GameStateManager()
		self.keyboardcontroller = Controller.KeyboardController()
		self.mousecontroller = Controller.MouseController()
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
		