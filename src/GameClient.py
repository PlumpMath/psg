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
import sys, cPickle, os

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
		
		self.maps               = []
		self.players            = []
		self.clientconnection   = ClientConnection()
		self.game               = Game()
		# These will be initialized upon starting the actual game
		self.viewstate          = None
		self.gamestatemgr       = None
		self.keyboardcontroller = None
		self.mousecontroller    = None
		self.gameFrame          = None
		
		# Load files
		for f in os.listdir('data/maps'):
			if os.path.splitext(f)[1] == '.map':
				try:
					fh = open('data/maps/' + f,'rb')
					map = cPickle.load(fh)
					self.maps.append(map)
					fh.close()
				except: print('Could not open file %s'%f)
		for f in os.listdir('data/players'):
			if os.path.splitext(f)[1] == '.plr':
				try:
					fh = open('data/players/' + f,'rb')
					player = cPickle.load(fh)
					self.players.append(player)
					fh.close()
				except: print('Could not open file %s'%f)
				
		#self.temp()
		
		# Load settings
		GameSettings().loadSettings()
		
		# Create GUI system
		self.gui = GUI(Keys(),theme=PSGTheme())
		
		# Show the main menu which will call start game
		self.menu = MainScreen(self, self.clientconnection)
		
		#self.startGame()
		
	def temp(self):
		from Map import SerializableMap
		from Player import SerializablePlayer
		
		
		p = SerializablePlayer(name="Chad the Destroyer", faction='Terrans', type='Human',
				 ai='None', gamesplayed=20, gameswon=10, gameslost=10)
		fh = open('data/players/' + p.name.replace(' ', ''),'wb')
		cPickle.dump(p, fh)
		fh.close()
		
		p = SerializablePlayer(name="Gorath", faction='Protath', type='ComputerAI',
				 ai='None', gamesplayed=20, gameswon=10, gameslost=10)
		fh = open('data/players/' + p.name.replace(' ', ''),'wb')
		cPickle.dump(p, fh)
		fh.close()
		
		p = SerializablePlayer(name="Chilrog", faction='Protath', type='ComputerAI',
				 ai='None', gamesplayed=20, gameswon=10, gameslost=10)
		fh = open('data/players/' + p.name.replace(' ', ''),'wb')
		cPickle.dump(p, fh)
		fh.close()
		
		m = SerializableMap()
		m.name = 'The Battle of Gorath'
		m.mapSize = (150,150,40)
		startingPlanets = 1
		
		m.addPlayer('Chad the Destroyer', faction='Terrans', type='Human', ai='None')
		m.addPlayer('Gorath', faction='Protath', type='Computer', ai='Gorath')
		m.addPlayer('Chilrog', faction='Protath', type='Computer', ai='Chilrog')
		
		m.addPlanet(self, (100,100,10), owner='Chad the Destroyer', rep='planet_01')
		m.addPlanet(self, (-100,-50,-30), owner='Gorath', rep='planet_01')
		m.addPlanet(self, (50,-100,0), owner='Chilrog', rep='planet_01')
		m.addPlanet(self, (20,20,20), owner='None', rep='planet_01')
		m.addPlanet(self, (-50,-100,-20), owner='None', rep='planet_01')
		m.addPlanet(self, (-20,-20,0), owner='None', rep='planet_01')
		m.addPlanet(self, (0,0,0), owner='None', rep='planet_01')
		
		m.addShip('LightCapture', pos=(110,110,10), hpr=(0,0,0), owner='Chad the Destroyer', rep='ship_03')
		m.addShip('LightCapture', pos=(-110,-50,-30), hpr=(0,0,0), owner='Gorath', rep='ship_03')
		m.addShip('LightCapture', pos=(50,-110,0), hpr=(0,0,0), owner='Chilrog', rep='ship_03')
		
		fh = open('data/maps/' + m.name.replace(' ', ''),'wb')
		cPickle.dump(m, fh)
		fh.close()
		
		
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
		#res = GameSettings().getSetting('RESOLUTION').split()[0].split('x')
		#self.xRes = int(res[0])
		#self.yRes = int(res[1])
		self.xRes = GameSettings().getSetting('X_RES')
		self.yRes = GameSettings().getSetting('Y_RES')
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
	
	
	
	
