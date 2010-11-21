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
from game.ClientConnection import ClientConnection
from game.GUI.Treegui.core import Gui
from game.GUI.Treegui.keys import Keys
from game.GUI.rtheme import RTheme
from game.GUI.mainmenu import MainScreen
from game.Settings import GameSettings
from game import Controller
from game import Event
from game import GameConsts
from game.GSEng import GSMgr
from game.GSEng.Map import *
from game.GXEng import GXMgr
from game.Util.Log import LogConsole

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
		
		# If AUTOSERVER is set automatically connect and start a game with the
		# local server
		#if (AUTOSERVER):
		#	def connResp(status):
		#		if status:
		#			# Authenticate
		#			self.clientconnection.authenticate('autoserver','password1', authResp)
		#		else:
		#			LOG.error("[GameClient] Could not autoconnect <%s>"%status)
		#	def authResp(status):
		#		if (status == 3):
		#			self.clientconnection.newGame("debug game", mapDict['id'], "3", newResp)
		#		else:
		#			LOG.error("[GameClient] Could not autoauthenticate <%s>"%status)
		#	def newResp(status):
		#		if status > 0:
		#			self.clientconnection.joinGame(status, joinResp)
		#		else:
		#			LOG.error("[GameClient] Could not automatically create a game <%s>"%status)
		#	def joinResp(status, mapMD5):
		#		if status == 2:
		#			Event.Dispatcher().broadcast(Event.Event('E_StartGame', src=self, data=mapMD5))
		#		else: 
		#			LOG.error("[GameClient] Could not autojoin <%s>"%status)
		#	# Use the debug map
		#	mapDict = self._mapStore.getMap(name="Debugger Map")
		#	# Connect
		#	self.clientconnection.connect('localhost', 9091, 3000, connResp)
		if NOSERVER:
			mapDict = self._mapStore.getMap(name="Debugger Map")
			print(mapDict)
			Event.Dispatcher().broadcast(Event.Event('E_StartGame', src=self, data=mapDict['id']))
		# Otherwise start menu GUI normally
		else:
			self.gui = Gui(Keys(),theme=RTheme())
			self.menu = MainScreen(self)
		
	def startGame(self, event):
		'''
			TODO - Document
		'''
		
		mapMD5 = event.data
		
		LOG.debug("[GameClient] Starting game with map ID %s"%mapMD5)
		
		if not NOSERVER:
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
		
		LOG.debug("[GameClient] Loading map id %s"%mapMD5)
		map = self._mapStore.loadMap(self._mapStore.getMap(mapMD5)['filename'])
		
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
		