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

# PSG imports
from ClientConnection import ClientConnection
#from GSEng.Game import Game
from GUI.Treegui.core import Gui
from GUI.Treegui.keys import Keys
from GUI.rtheme import RTheme
from GUI.mainmenu import MainScreen
from Settings import GameSettings
import Controller
import Event
import GameConsts
from GSEng import GSMgr
from GSEng.Map import *
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
		
		self._mapStore = MapStore()
		
		# Start menu GUI
		self.gui = Gui(Keys(),theme=RTheme())
		self.menu = MainScreen(self)
		
	def startGame(self, event):
		'''
			TODO - Document
		'''
		
		mapMD5 = event.data
		
		LOG.debug("[GameClient] Starting game with map ID %s"%mapMD5)
		
		self.gui.clear()
		del(self.menu)
		del(self.gui)
		
		# Create GSM
		self.gsm = GSMgr.GSMgr(self.clientconnection)
		
		# Setup controls
		self.keyboardcontroller = Controller.KeyboardController()
		self.mousecontroller = Controller.MouseController()
		
		# Create GXEng
		self.gxm = GXMgr.GXMgr()
		self.gxm.makeGameEngine()
		
		self.gsm.registerGXEng(self.gxm)
		
		#self.gamestate.loadGame(self.curr_game)
		#self.gameFrame = GameWindow()
		LOG.debug("[GameClient] Loading map id %s"%mapMD5)
		map = self._mapStore.loadMap(self._mapStore.getMap(mapMD5)['filename'])
		#self.gxm.loadMap(map)
		self.gsm.startGame(map)
		
	def exitGame(self, event):
		''' Clean up open/running game. Show mainmenu.'''
		LOG.debug("[GameClient] Exiting game")
		self.gui = Gui(Keys(),theme=RTheme())
		self.menu = MainScreen(self)
		
	def exitProgram(self, event):
		'''
			TODO - Document
		'''
		LOG.debug("[GameClient] Exiting process")
		# do any necessary cleanup
		if self.clientconnection.isConnected():
			self.clientconnection.disconnect(None)
		sys.exit(0)
		