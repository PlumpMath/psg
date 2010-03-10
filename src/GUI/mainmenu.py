''' mainmenu.py
	
	Sets up and manages all the main menus and related functions.
	
	Author:			Chad Rempp
	Date:			2009/05/15
	License:		GNU LGPL v3
	Todo:			This is a HUGE mess! Clean this up.
'''

# Python imports
import os

# Panda imports
from direct.gui.OnscreenImage import OnscreenImage

# PSG imports
from ClientConnection import ClientConnection
#import GUI
from GUI.Treegui.components import *
from GUI.Treegui.widgets import *
from GUI.Treegui.core import Gui
from Settings import GameSettings
import Event
from GameConsts import *
from Util.Log import LogConsole
from GSEng.Map import *

# These are global because they are needed deep within nested structures and
# it's annoying to embed them that deep
MENUSIZE = Vec2(420,300)
MENUPAD  = Vec4(20,20,18,0) # (l,r,t,b)
x_res = base.win.getProperties().getXSize()
y_res = base.win.getProperties().getYSize()
MENUPOS  = Vec2((x_res-MENUSIZE[0])/2,
			   (y_res-MENUSIZE[1])/2+40)

class Dialog(Pane):
	''' Dialog box helper class'''
	def __init__(self):
		Pane.__init__(self)
		self.x = 200
		self.y = 20
		self.width = 240
		self.height = 90
		self.text = ''
		self.button = self.add(Button("cancel",self.ok,pos=(10,60),size=(100,12)))
	
	def ok(self):
		self.visible = False
		gui.remove(self)
		del(self)
		
class SelList(SingleSelectList):
	''' A slightly modified SingleSelectList
	
		This selection list provides methods to add and remove items.
	'''
	def __init__(self,options,*args,**kargs):
		SingleSelectList.__init__(self, options, *args,**kargs)
		self.buttons = []
		self.selectedButton = None
		
	def addOption(self,option):
		i = len(self.buttons)
		button = ValueButton(
				option, 
				i,
				onSelect=self.setSelectedOption, 
				pos = Vec2(10,10+int(i)*25), 
				size = Vec2(self.width-40,15))
		self.add(button)
		self.buttons.append(button)
	
	def delOption(self,option):
		# Rebuild button list so values and positions are all updated
		newButtons = []
		i = 0
		for b in self.buttons:
			self.remove(b)
			if b.text is not option:
				b.value = i
				b.pos = Vec2(10,10+int(i)*25)
				self.add(button)
				newButtons.append(button)
		self.buttons = newButtons
	
	def clearOptions(self):
		#print self.children
		for b in self.buttons:
			b.visible = False
			#self.remove(b)
		self.buttons = []
	
	def setSelectedOption(self, value):
		""" selects a button with the option """
		if self.selectedButton:
			self.selectedButton.color = (1,1,1,1)
		for i,button in enumerate(self.buttons):
			if button.value == value:
				self.selected = i
				self.option = button.text
				self.value = value
				self.selectedButton = button
				self.selectedButton.color = (.4,.4,.4,1)
				self.onSelect()
				return True
				
	def onSelect(self):
		#print("Selected %s"%self.value)
		pass

class MainScreen(object):
	''' Controls the main menu screen. This is not the actual main menu, this
		object controls movement between the main menu forms'''
	
	def __init__(self, gcli):
		''' Create the menu forms and draw the background image. The main
			menu also handles changing the current active form.'''
		
		LOG.notice("Creating Main Menu")
		
		#Create handle to game client
		self.gcli = gcli
		
		#self.menusize = MENUSIZE
		#self.MENUPAD  = MENUPAD 
		#self.menupos  = MENUPOS
		
		#self.gameList   = []
		
		# Background image
		self.background = OnscreenImage(image = 'data/images/menubackground2.png',
		  					pos=(0.6,0,-1.1333),
		  					scale=(1.6,1,2.1333),
		  					parent=render2d)
		
		# Create menu forms
		self.main = MainPane(self, gcli)
		gui.add(self.main)
				
		self.multi = MultiPane(self, gcli)
		gui.add(self.multi)
		self.multi.visable = False

		self.option = OptionPane(self, gcli)
		gui.add(self.option)
		self.option.visable = False
		
		self.player = PlayerPane(self, gcli)
		gui.add(self.player)
		self.player.visable = False
		
		self.credit = CreditsPane(self, gcli)
		gui.add(self.credit)
		self.credit.visable = False
		
		# Setup menu state
		self._currentmenu  = self.main
		
	def showMain(self):
		self._currentmenu.toggle()
		self._currentmenu = self.main
		self.main.toggle()
		
	def showMulti(self):
		self._currentmenu.toggle()
		self._currentmenu = self.multi
		self.multi.toggle()
	
	def showPlayer(self):
		self._currentmenu.toggle()
		self._currentmenu = self.player
		self.player.toggle()
	
	def showOptions(self):
		self._currentmenu.toggle()
		self._currentmenu = self.option
		self.option.toggle()
	
	def showCredits(self):
		self._currentmenu.toggle()
		self._currentmenu = self.credit
		self.credit.toggle()
	
	def exit(self):
		Event.Dispatcher().broadcast(Event.Event('E_ExitProgram',src=self))
		
	def startGame(self, mapMD5):
		''' Clean up all the menus and then tell dispatcher to start the game'''
		self.background.destroy()
		Event.Dispatcher().broadcast(Event.Event('E_StartGame', src=self, data=mapMD5))

class MainPane(Pane):
	def __init__(self, parent, gcli):
		Pane.__init__(self)
		self.gcli = gcli
		self.x = MENUPOS[0] 
		self.y = MENUPOS[1]
		self.width = MENUSIZE[0]
		self.height = MENUSIZE[1]
		
		self.add(Button('Network Game',
						parent.showMulti,
						pos=(140,40),
						size=(120,20),
						point=16));
		self.add(Button('Player Setup',
						parent.showPlayer,
						pos=(140,80),
						size=(120,20),
						point=16));
		self.add(Button('Options',
						parent.showOptions,
						pos=(140,120),
						size=(120,20),
						point=16));
		self.add(Button('Credits',
						parent.showCredits,
						pos=(140,160),
						size=(120,20),
						point=16));
		self.add(Button('Exit',
						parent.exit,
						pos=(140,200),
						size=(120,20),
						point=16));

		
class MultiPane(Pane):
	class createPane(Pane):
		def __init__(self, parent):
			self._parent = parent
			Pane.__init__(self)
			self._clientcon = ClientConnection()
			self.x = MENUPOS[0] 
			self.y = MENUPOS[1]
			self.width = MENUSIZE[0]
			self.height = MENUSIZE[1]
			
			DEBUG_NAME = "Test Game"
			
			self.add(Label("NEW NETWORK GAME",
						   pos=(160,1)))
			self.add(Label("Name",
						   pos=(MENUPAD[0],MENUPAD[2])))
			self.i_name = self.add(Entry(DEBUG_NAME,
										 pos = (MENUPAD[0]+140, MENUPAD[2]),
										 size = (220,10)))
			self.add(Label("Number of Players",
						   pos=(MENUPAD[0],MENUPAD[2]+25)))
			self.i_num = self.add(Entry("3",
										 pos = (MENUPAD[0]+140, MENUPAD[2]+25),
										 size = (40,10)))
			self.add(Label("Map",
						   pos=(MENUPAD[0]+160,MENUPAD[2]+50)))
			self.s_maps = self.add(SelList([],
										   pos=(MENUPAD[0],MENUPAD[2]+75),
										   size=(MENUSIZE[0]-MENUPAD[2]-5,150)))
			self.add(Button("Ok",
							self._ok,
							pos=(MENUPAD[0],MENUSIZE[1]-MENUPAD[3]-20),
							size=(100,12)))
			self.add(Button("Cancel",
							self._cancel,
							pos=(MENUSIZE[0]-120,MENUSIZE[1]-MENUPAD[3]-20),
							size=(100,12)))
			
			self._mapStore = MapStore()
			self._refreshMaps()
			
			
		def _ok(self):
			self.createDialog = gui.add(Dialog())
			if (self.i_name.text is ''):
				self.createDialog.text = "Please enter a name for the game"
				self.createDialog.button.text = "ok"
			elif (self.i_num.text is '' or int(self.i_num.text) > MAX_GAME_PLAYERS):
				self.createDialog.text = "Invalid number of players"
				self.createDialog.button.text = "ok"
			elif (self.s_maps.getSelectedOption() is None):
				self.createDialog.text = "Please select a map"
				self.createDialog.button.text = "ok"
			else:
				self.createDialog.text = "Creating game."
				#print(self._mapStore)
				mapName = self.s_maps.buttons[self.s_maps.getSelectedOption()].text
				#print(mapName)
				mapDict = self._mapStore.getMap(name=mapName)
				
				print("id=%s"%mapDict['id'])
				if mapDict is not None:
					self._clientcon.newGame(self.i_name.text, mapDict['id'], self.i_num.text, self._createResponse)
				else:
					self.createDialog.text = "Cannot load selected map"
					LOG.error("[createPane] Cannot load selected map")
		
		def _createResponse(self, status):
			print("Resp=%s"%status)
			if status > 0:
				self.createDialog.ok()
				self._parent._refreshGames()
				self._cancel()
			else:
				self.createDialog.text = "Error creating game"
				LOG.error("[createPane] Error creating game")
		
		def _cancel(self):
			self._parent.visible = True
			self.visible = False
			gui.remove(self)
			del(self)
			
		def _refreshMaps(self):
			self._mapStore.rescan()
			mapList = self._mapStore.getAvailableNames()
			for b in self.s_maps.buttons:
				self.remove(b)
			for m in mapList:
				self.s_maps.addOption(m)
		
	def __init__(self, parent, gcli):
		Pane.__init__(self)
		self._widgetClickers = dict()
		self._parent = parent
		self._gcli = gcli
		self.x = MENUPOS[0] 
		self.y = MENUPOS[1]
		self.width = MENUSIZE[0]
		self.height = MENUSIZE[1]
		self._clientcon = ClientConnection()
		self._mapStore = MapStore()
		
		server = self._clientcon.address
		port = self._clientcon.port
		
		# Connection
		self.add(Label("NETWORK GAME",
					   pos=(160,1)))
		self.add(Label("Server:",
					   pos=(MENUPAD[0],MENUPAD[2])))
		self.i_server = self.add(Entry(server,
									   pos = (MENUPAD[0]+65, MENUPAD[2]),
									   size = (120,10)))
		self.add(Label("Port:",
					   pos=(MENUPAD[0]+200,MENUPAD[2])))
		self.i_port = self.add(Entry(port,
									 pos = (MENUPAD[0]+265, MENUPAD[2]),
									 size = (120,10)))
		self.add(Label("Username:",
					   pos=(MENUPAD[0],MENUPAD[2]+25)))
		self.i_username = self.add(Entry(DEFAULT_USERNAME,
										 pos = (MENUPAD[0]+65, MENUPAD[2]+25),
										 size = (120,10)))
		self.add(Label("Password:",
					   pos=(MENUPAD[0]+200,MENUPAD[2]+25)))
		self.i_password = self.add(PasswordEntry(DEFAULT_PASSWORD,
												 pos = (MENUPAD[0]+265, MENUPAD[2]+25),
												 size = (120,10)))
		
		self.b_connect = self.add(Button("Connect",
								  self._connect,
								  pos=(MENUSIZE[0]-90,MENUPAD[2]+50),
								  size=(70,12)))
		
		self.s_games = self.add(SelList([],
										pos=(MENUPAD[0],MENUPAD[2]+75),
										size=(MENUSIZE[0]-MENUPAD[2]-5,150)))
		
		self.b_create = self.add(Button("Create Game",
										self._create,
										pos=(MENUPAD[0],MENUSIZE[1]-MENUPAD[3]-45),
										size=(100,12)))
		self._disable(self.b_create)
		
		self.add(Button("Join Game",
						self._join,
						pos=(MENUSIZE[0]-MENUPAD[1]-95,MENUSIZE[1]-MENUPAD[3]-45),
						size=(100,12)))
		
		self.add(Button("Main Menu",
						parent.showMain,
						pos=(MENUPAD[0],MENUSIZE[1]-MENUPAD[3]-20),
						size=(100,12)))
		
		if self._clientcon.isAuthorized():
			self._setConnected()
		
	def _setConnected(self, status=None):
		self._disable(self.i_server)
		self._disable(self.i_port)
		self._disable(self.i_username)
		self._disable(self.i_password)
		self._enable(self.b_create)
		self.b_connect.text = "Disconnect"
		self.b_connect.onClick = self._disconnect
	
	def _setDisconnected(self, status=None):
		self._enable(self.i_server)
		self._enable(self.i_port)
		self._enable(self.i_username)
		self._enable(self.i_password)
		self._disable(self.b_create)
		self.b_connect.text = "Connect"
		self.b_connect.onClick = self._connect
	
	def _disable(self, widget):
		widget.color = (.4,.4,.4,1)
		self._widgetClickers[widget] = widget.onClick
		widget.onClick = lambda: None
		
	def _enable(self, widget):
		widget.color = (1,1,1,1)
		widget.onClick = self._widgetClickers[widget]
		
	def _disconnect(self):
		''' Disconect from the server'''
		self._clientcon.disconnect(self._setDisconnected)
	
	def _refreshGames(self):
		'''Request list of available games from server and populate list'''
		LOG.debug('[MultiPane] Updating games')
		
		def onResp(games):
			for g in games:
				self.s_games.addOption("%s - %s"%(g['id'],g['name']))
		
		self.s_games.clearOptions()
		
		self._clientcon.getGameList(onResp)
	
	def _connect(self):
		''' Connect to a server using the info filled in on this form.'''
		connectDialog = None
		connected     = False
		authenticated = False
		
		def connectionResponse(resp):
			if resp:
				connectDialog.text = 'Connected to the server,\nauthenticating...'
				LOG.notice("[MultiPane] Connected to the server, authenticating...")
				self._clientcon.authenticate(username, password, authResponse)
			else:
				connectDialog.text = 'Connection failed.'
				connectDialog.button.text = "ok"
				
		def authResponse(resp):
			if (resp == 0):
				connectDialog.text = 'Authentication failed.'
				LOG.error("[MultiPane] Authentication failed")
				connectDialog.button.text = "ok"
			elif (resp == 1):
				connectDialog.text = 'You are already connected.'
				LOG.error("[MultiPane] You are already connected")
				self._setConnected()
				connectDialog.button.text = "ok"
			elif (resp == 2):
				connectDialog.text = 'Incorrect password.'
				LOG.error("[MultiPane] Incorrect password")
				connectDialog.button.text = "ok"
			elif (resp == 3):
				connectDialog.text = 'Authenticated.\nYou are connected.'
				LOG.notice("[MultiPane] Authenticated. You are connected")
				self._setConnected()
				self._refreshGames()
				connectDialog.button.text = "ok"
				#self.updateGameList()
			
		LOG.notice("[MultiPane] connecting server=%s port=%s user=%s, pass=%s"%(self.i_server.text, self.i_port.text, self.i_username.text, self.i_password.password))
		
		# Get the values from the form
		server   = self.i_server.text
		username = self.i_username.text
		password = self.i_password.text
		port     = self.i_port.text
		
		# If everything is ok attempt to connect and use connectDialog to show the status
		if (server!='' and username!='' and password!='' and port!=''):
			self._clientcon.address = server
			connectDialog = gui.add(Dialog())
			connectDialog.text = "connecting to server %s"%server
			LOG.notice("[MultiPane] Connecting to server %s"%server)
			self._clientcon.connect(server, int(port), 3000, connectionResponse)
		else:
			LOG.error('[MultiPane] You did not fill in the all the values')
			connectDialog = gui.add(Dialog())
			connectDialog.text = "Please fill in all the values."
	
	def _create(self):
		self.visible = False
		cPane = self.createPane(self)
		gui.add(cPane)
		
	def _join(self):
		''' Join the selected game
			
			The only way I can think of attaching the game ID to the selection
			list is in the button text so now we need to extract it.
		'''
		def response(status, mapMD5):
			if (status == 0):
				joinDialog.text = "could not find the game"
				LOG.error("[MultiPane] Could not find the game")
			elif (status == 1):
				joinDialog.text = "the game is full"
				LOG.error("[MultiPane] The game is full")
			elif (status == 2):
				if self._mapStore.isAvailable(id=mapMD5):
					joinDialog.visible = False
					self._parent.startGame(mapMD5)
				else:
					joinDialog.text = "downloading map..."
					LOG.notice("[MultiPane] downloading map...")
					downloadMap(mapMD5)
			else:
				joinDialog.text = "unknown error"
				LOG.error("[MultiPane] Unknown error")
		
		def downloadResp(status, mapMD5):
			if (status == 0):
				joinDialog.text = "download failed."
				LOG.error("[MultiPane] download failed")
			elif (status == 1):
				self._parent.startGame(mapMD5)
			else:
				joinDialog.text = "unknown error"
				LOG.error("[MultiPane] Unknown error")
				
		def downloadMap(id):
			self._clientcon.downloadMap(id, callback)
			
		if (self.s_games.getSelectedOption() is not None):
			gameString = self.s_games.buttons[self.s_games.getSelectedOption()].text
			gameID = int(gameString.split('-')[0].strip())
			joinDialog = gui.add(Dialog())
			joinDialog.text = "joining game '%s'"%gameString
			LOG.notice("[MultiPane] joining game '%s'"%gameString)
			self._clientcon.joinGame(gameID, response)
		
class OptionPane(Pane):
	def __init__(self, parent, gcli):
		Pane.__init__(self)
		self._parent = parent
		self.gcli = gcli
		self.x = MENUPOS[0] 
		self.y = MENUPOS[1]
		self.width = MENUSIZE[0]
		self.height = MENUSIZE[1]
		
class SinglePane(Pane):
	def __init__(self, parent, gcli):
		Pane.__init__(self)
		self._parent = parent
		self.gcli = gcli
		self.x = MENUPOS[0] 
		self.y = MENUPOS[1]
		self.width = MENUSIZE[0]
		self.height = MENUSIZE[1]
		
class PlayerPane(Pane):
	def __init__(self, parent, gcli):
		Pane.__init__(self)
		self._parent = parent
		self.gcli = gcli
		self.x = MENUPOS[0] 
		self.y = MENUPOS[1]
		self.width = MENUSIZE[0]
		self.height = MENUSIZE[1]
		
class CreditsPane(Pane):
	def __init__(self, parent, gcli):
		Pane.__init__(self)
		self._parent = parent
		self.gcli = gcli
		self.x = MENUPOS[0] 
		self.y = MENUPOS[1]
		self.width = MENUSIZE[0]
		self.height = MENUSIZE[1]