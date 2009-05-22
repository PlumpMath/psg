''' GameClient.py
	Author:			Chad Rempp
	Date:			2009/05/07
	Purpose:		The game client initializes all the game models.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			TODO - Make the PSGClient a singleton.
'''

# Python imports
import sys

# Panda imports
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import FrameBufferProperties
from pandac.PandaModules import GraphicsPipe
from pandac.PandaModules import WindowProperties

# PSG imports
#from data.themes.psgtheme import PSGTheme
from Settings import GameSettings
import Event
import Controller
import GameStateMgr
import View
import ViewStateMgr
from gui.core import GUI
from gui.keys import Keys
from gui.psgtheme import PSGTheme
from gui.mainmenu import MainScreen
from ClientConnection import ClientConnection

class GameClient(DirectObject):
	'''Initialize the client. Loads settings, shows the main game menu, sets up and runs the game'''
	def __init__(self):
		print("Starting PSG Client ...")
		# Initialize event dispatcher
		self._dispatcher = Event.Dispatcher()
		self._dispatcher.register(self, 'E_ExitGame', self.exitGame)
		self._dispatcher.register(self, 'E_ExitProgram', self.exitProgram)
		
		# These will be initialized upon starting the actual game
		self.viewstate          = None
		self.gamestatemgr       = None
		self.keyboardcontroller = None
		self.mousecontroller    = None
		self.gameFrame          = None
		self.clientconnection   = ClientConnection()
		self.game               = Game()
		
		# Load settings
		GameSettings().loadSettings()
		
		# Create GUI system
		self.gui = GUI(Keys(),theme=PSGTheme())
		
		# Show the main menu which will call start game
		self.menu = MainScreen(self.game, self.clientconnection)
		
		#self.startGame()
		
	def createGame(self):
		''' If we are playing a single player game or hosting a multiplayer game
			we must first create the game.'''
		if (self._gameType == 'Multiplayer'):
			# Create the game and submit it to the server
			print('Creating a multiplayer game')
		elif (self._gameType == 'Singleplayer'):
			print('Creating a singleplayer game')
			
	def loadGame(self, file):
		'''Load a saved game from a file'''
		pass
		
	def makeGameEngine(self):
		''' Creates a new game engine based on settings in GameSettings.
			Information for this came from here
			http://panda3d.org/phpbb2/viewtopic.php?t=2848'''
		# Setup values from gamesettings
		res = GameSettings().getSetting('RESOLUTION').split()[0].split('x')
		self.xRes = int(res[0])
		self.yRes = int(res[1])
		aa    = int(GameSettings().getSetting('ANTIALIAS'))
		alpha = int(GameSettings().getSetting('ALPHABITS'))
		color = int(GameSettings().getSetting('COLORDEPTH'))
		
		# Create a new FrameBufferProperties object using our settings
		fbProps = FrameBufferProperties()
		fbProps.addProperties(FrameBufferProperties.getDefault())
		fbProps.setMultisamples(aa)
		fbProps.setAlphaBits(alpha)
		fbProps.setDepthBits(color)
		
		# Create a WindowProperties object
		winProps = WindowProperties( base.win.getProperties() )
		if GameSettings().getSetting('FULLSCREEN') == 'True':
			winProps.setFullscreen(True)
			winProps.setUndecorated(True)
		else:
			winProps.setFullscreen(False)
		winProps.setSize(self.xRes,self.yRes)
		winProps.setTitle('PSG - Project Space Game: Alpha')
		
		# Create the engine
		base.graphicsEngine.makeOutput(base.pipe, 'mainGameOutput', 0, fbProps, winProps,  GraphicsPipe.BFRequireWindow, base.win.getGsg())
		base.openMainWindow(props=winProps, gsg=base.win.getGsg(), keepCamera=1) 

		base.camLens.setFov(60.0)
			
	def startGame(self):
		# Some of this will be moved to createGame / loadGame
		self.makeGameEngine()
		if GameSettings().getSetting('SHOWFPS') == "True":
			base.setFrameRateMeter(True)
		
		self.viewstate = ViewStateMgr.ViewStateManager()
		self.viewstate.addView(View.GameView())
		#self.viewstate.addView(View.ConsoleView())
		self.gamestate = GameStateMgr.GameStateManager()
		self.keyboardcontroller = Controller.KeyboardController()
		self.mousecontroller = Controller.MouseController()
		self.gamestate.newGame()
		#self.gameFrame = GameWindow()
		
	def exitGame(self, event):
		''' Clean up open/running game. Show mainmenu.'''
		pass
		
	def exitProgram(self, event):
		# do any necessary cleanup
		if self.clientconnection.isConnected():
			self.clientconnection.disconnect(None)
		sys.exit(0)
		
class Game:
	gametype = 'Single'
	gamemap = None
	players = None
	server  = None
	
	
	
	
