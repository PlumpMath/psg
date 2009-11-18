''' mainmenu.py
	Author:			Chad Rempp
	Date:			2009/05/15
	Purpose:		Sets up and manages all the main menus and related functions.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			This is a HUGE mess! Clean this up.
'''

# Python imports
import os

# PSG imports
from direct.gui.OnscreenImage import OnscreenImage
from gui.keys import Keys
from gui.controls import *
from gui.widgets import *
from Settings import GameSettings
import Event
import Map
import Player

# Set current screen resolution
x_res = base.win.getProperties().getXSize()
y_res = base.win.getProperties().getYSize()

#_MAINSCREEN_CLASS_____________________________________________________________
class MainScreen:
	''' Controls the main menu screen. This is not the actual main menu, this
		object controls movement between the main menu forms'''
	
	# Size of the menu forms
	menusize = Vec2(420,300)
	menupad  = Vec4(20,20,30,0) # (l,r,t,b)
	
	_currentmenu = None
	
	def __init__(self):
		''' Create the menu forms and draw the background image. The main
			menu also handles changing the current active form.'''
		
		print ("MAINSCREEN")
		
		self.menupos    = Vec2((x_res-self.menusize[0])/2,(y_res-self.menusize[1])/2+40)
		self.gameList   = []
		
		# Background image
		self.background = OnscreenImage(image = 'data/images/menubackground.png',
		  					pos=(0.6,0,-1.1333),
		  					scale=(1.6,1,2.1333),
		  					parent=render2d)
		
		# Create menu forms
		self.main = MainForm(self)
		gui.add(self.main)
		
		self.single = SingleForm(self)
		gui.add(self.single)
		self.single.toggle()
		
		self.multi = MultiForm(self)
		gui.add(self.multi)
		self.multi.toggle()
		
		self.option = OptionForm(self)
		gui.add(self.option)
		self.option.toggle()
		
		self.player = PlayerForm(self)
		gui.add(self.player)
		self.player.toggle()
		
		self.credit = CreditsForm(self)
		gui.add(self.credit)
		self.credit.toggle()
		
		# Setup menu state
		self._currentmenu  = self.main
		
	def showMain(self, button, key, mouse):
		self._currentmenu.toggle()
		self._currentmenu = self.main
		self.main.toggle()
	
	def showSingle(self, button, key, mouse):
		self._currentmenu.toggle()
		self._currentmenu = self.single
		self.single.toggle()
		
	def showMulti(self, button, key, mouse):
		self._currentmenu.toggle()
		self._currentmenu = self.multi
		self.multi.toggle()
	
	def showPlayer(self, button, key, mouse):
		self._currentmenu.toggle()
		self._currentmenu = self.player
		self.player.toggle()
	
	def showOptions(self, button, key, mouse):
		self._currentmenu.toggle()
		self._currentmenu = self.option
		self.option.toggle()
	
	def showCredits(self, button, key, mouse):
		self._currentmenu.toggle()
		self._currentmenu = self.credit
		self.credit.toggle()
	
	def exit(self, button, key, mouse):
		print('exit')
		Event.Dispatcher().broadcast(Event.Event('E_ExitProgram',src=self))
		
	def startGame(self):
	#	print('Start game:')
		self.background.destroy()
		self.main.hide()
		self.single.hide()
		self.multi.hide()
		del(self.main)
		del(self.single)
		del(self.multi)
		gcli.startGame()

class MainForm(Form):
	''' The main game menu'''
	def __init__(self, prnt):
		Form.__init__(self,'Main Menu',pos=prnt.menupos, size=prnt.menusize)
		
		self.prnt = prnt
		
		# Dont show close or sizer button and disable drag.
		self.x.node.hide()
		self.sizer.node.hide()
		self.things[0].onClick=lambda b,k,m : None
		
		self.add(Button('Single Player',
				pos=Vec2(150,40),
				size=(80,20),
				point=16,
				onClick=self.prnt.showSingle));
		self.add(Button('Multi Player',
				pos=Vec2(150,80),
				size=(80,20),
				point=16,
				onClick=self.prnt.showMulti));
		self.add(Button('Player Setup',
				pos=Vec2(150,120),
				size=(80,20),
				point=16,
				onClick=self.prnt.showPlayer));
		self.add(Button('Options',
				pos=Vec2(150,160),
				size=(80,20),
				point=16,
				onClick=self.prnt.showOptions));
		self.add(Button('Credits',
				pos=Vec2(150,200),
				size=(80,20),
				point=16,
				onClick=self.prnt.showCredits));
		self.add(Button('Exit',
				pos=Vec2(150,240),
				size=(80,20),
				point=16,
				onClick=self.prnt.exit));
		
class SingleForm(Form):
	''' Single player game menu.'''
	def __init__(self, prnt):
		Form.__init__(self,'Singleplayer Game',pos=prnt.menupos, size=prnt.menusize)
		self.prnt = prnt
		self.numPlayerRange = range(1,5)
		self.numPlayerRange.reverse()
		#self.playerDropDowns = []
		#self.d_map = None
		
		# Dont show close or sizer button and disable drag.
		self.x.node.hide()
		self.sizer.node.hide()
		self.things[0].onClick=lambda b,k,m : None
		
		# Setup defaults
		if len(gcli.availableMaps.values()) > 0:
			defaultMap = gcli.availableMaps.values()[0]
		else:
			defaultMap = ''
		if len(gcli.availablePlayers.values()) > 0:
			defaultPlayer = gcli.availablePlayers.values()[0]
		else:
			defaultPlayer = ''
			
		# Draw widgets from bottom to top (this is for dropdown menu sort order)
		self.add(Button('Main Menu',
				pos=Vec2(self.prnt.menupad[0],
						 self.prnt.menusize[1]-self.prnt.menupad[3]-20),
				onClick=self.prnt.showMain))
		self.add(Button('Start Game',
				pos=Vec2(self.prnt.menusize[0]-self.prnt.menupad[1]-50,
						 self.prnt.menusize[1]-self.prnt.menupad[3]-20),
				onClick=self.startGame))
		
		# TODO - make the following dependent on the number of players in the
		# current map. This will likely require a scrolled section
		self.playerDropDowns = list()
		for i in self.numPlayerRange:
			self.add(Lable('Player ' + str(i),
					pos=Vec2(self.prnt.menupad[0],
							 self.prnt.menupad[2]+30+(30*i))))
			p = DropDown(gcli.availablePlayers.values(),
					defaultPlayer,
					pos=Vec2(self.prnt.menupad[0]+60,
							 self.prnt.menupad[2]+30+(30*i)))
			t = DropDown(['Human','Computer'],
					'Computer',
					pos=Vec2(self.prnt.menupad[0]+220,
							 self.prnt.menupad[2]+30+(30*i)))
			self.playerDropDowns.append((p,t))
			self.add(p)
			self.add(t)
			
		print("playerDropDowns size=%s"%len(self.playerDropDowns))
		self.add(Lable('Map',
				pos=Vec2(self.prnt.menupad[0],
						 self.prnt.menupad[2])))
		self.d_map = DropDown(gcli.availableMaps.values(),
				defaultMap,
				pos=Vec2(self.prnt.menupad[0]+50,
						 self.prnt.menupad[2]),
				size=Vec2(280,20))
		self.add(self.d_map)
		
	def startGame(self, button=None, key=None, mouse=None):
		''' Put together the game and tell gameclient to start it.'''
		gcli.curr_game.id         = 0
		gcli.curr_game.name       = "Test Game"
		for d in self.playerDropDowns:
			pass
			# Create player
			name = d[0].getOption()
			print(name)
			p = Player.getPlayer(name=name)
			gcli.curr_game.players.append(p)
		gcli.curr_game.maxPlayers = 5
		gcli.curr_game.mapName    = self.d_map.getOption()
		gcli.curr_game.mapFileName= Map.getMapFileName(gcli.curr_game.mapName)
		#gcli.curr_game.startTime  = starttime
		gcli.curr_game.turnNumber = 0
		
		self.prnt.startGame()
		
	def newSelectedMap(self):
		pass

class MultiForm(Form):
	''' Multi player game menu.'''
	def __init__(self, prnt):
		Form.__init__(self,'Multiplayer Game',pos=prnt.menupos, size=prnt.menusize)
		self.prnt = prnt
		
		# Dont show close or sizer button and disable drag.
		self.x.node.hide()
		self.sizer.node.hide()
		self.things[0].onClick=lambda b,k,m : None
		
		# Default values
		server   = gcli.clientconnection.getAddress()
		username = 'chad'
		password = 'password1'
		port     = gcli.clientconnection.getPort()
		games    = [] # List of game description strings
		for g in self.prnt.gameList:
			games.append(g.description)
		
		# Draw controls for this form
		self.add(Lable('Username:',
				pos=Vec2(self.prnt.menupad[0],
				 		self.prnt.menupad[2])))
		self.i_username = Input(username,
				pos=Vec2(self.prnt.menupad[0]+60,
						 self.prnt.menupad[2]))
		self.add(self.i_username)
		self.add(Lable('Password:',
				pos=Vec2(self.prnt.menupad[0]+200,
						 self.prnt.menupad[2])))
		self.i_password = Input(password,
				pos=Vec2(self.prnt.menupad[0]+260,
						 self.prnt.menupad[2]))
		self.add(self.i_password)
		self.add(Lable('Server:',
				pos=Vec2(self.prnt.menupad[0],
						 self.prnt.menupad[2]+25)))
		self.i_server = Input(server,
				pos=Vec2(self.prnt.menupad[0]+60,
						 self.prnt.menupad[2]+25),
				size=Vec2(130,20))
		self.add(self.i_server)
		self.add(Lable('Port:',
				pos=Vec2(self.prnt.menupad[0]+200,
						 self.prnt.menupad[2]+25)))
		self.i_port = Input(port,
				pos=Vec2(self.prnt.menupad[0]+260,
						 self.prnt.menupad[2]+25),
				size=Vec2(130,20))
		self.add(self.i_port)
		self.add(Button('Create Game',
				pos=Vec2(self.prnt.menupad[0],
						 self.prnt.menupad[2]+50),
				onClick=self.createGame))
		self.add(Button('Connect',
				pos=Vec2(self.prnt.menusize[0]-90,
						 self.prnt.menupad[2]+50),
				onClick=self.connect))
		self.add(Lable('Games:',
				pos=Vec2(self.prnt.menupad[0],
						 self.prnt.menupad[2]+70)))
		self.l_games = SelectList(games,
				pos=Vec2(self.prnt.menupad[0],
						 self.prnt.menupad[2]+90),
				size=Vec2(200,200))
		self.add(self.l_games)
		self.add(Button('Main Menu',
				pos=Vec2(self.prnt.menupad[0],
						 self.prnt.menusize[1]-self.prnt.menupad[3]-20),
				onClick=self.prnt.showMain))
		self.add(Button('Join',
				pos=Vec2(self.prnt.menusize[0]-self.prnt.menupad[1]-50,
						 self.prnt.menusize[1]-self.prnt.menupad[3]-20),
				onClick=self.joinGame))
	
	def updateGameList(self):
		''' Request game list from the server and update the local list upon
			response.'''
		print("updating game list now")
		def response(games):
			self.prnt.gameList = games
			self.l_games.clear()
			for g in games:
				self.l_games.addOption(g.description)
		gcli.clientconnection.getGameList(response)
		
	def createGame(self, button, key, mouse):
		''' Create a dialog to gather info on the game to create.'''
		print('create game')
		createGameDialog = None
				
		def onOk(button, key, mouse):
			''' Assemle the game data and send it to the server.'''
			print('Ok')
			gameName    = createGameDialog.i_name.getText()
			mapName     = createGameDialog.d_map.getOption()
			mapFileName = Map.getMapFileName(mapName)
			maxPlayers  = createGameDialog.i_maxplayers.getText()
			gcli.clientconnection.newGame(gameName, mapName, mapFileName, maxPlayers, createResponse)
			
		def onCancel(button, key, mouse):
			print('Cancel')
			createGameDialog.toggle()
			gui.remove(createGameDialog)
			
		def createResponse(resp):
			''' Handle response from create game request.'''
			print('Game created, updating list')
			if (resp):
				createGameDialog.l_status.setText('Game created, id %d'%resp)
				# Make ok button exit dialog
				createGameDialog.setOkFunc(onCancel)
				self.updateGameList()
			else:
				createGameDialog.l_status.setText('Could not create game')
				# Make ok button exit dialog
				createGameDialog.setOkFunc(onCancel)
		
		if gcli.clientconnection.isConnected():
			createGameDialog = CreateGameDialog(self.prnt, okFunc=onOk, cancelFunc=onCancel)
			gui.add(createGameDialog)
		else:
			createGameDialog = Alert('Oops!', text='Can not create game, we are not connected', pos=Vec2(250,20))
			gui.add(createGameDialog)
		
	def connect(self, button, key, mouse):
		''' Connect to a server using the info filled in on this form.'''
		connectDialog = None
		connected     = False
		authenticated = False
		
		def connectionResponse(resp):
			if resp:
				connectDialog.setText('Connected to the server, authenticating...')
				gcli.clientconnection.authenticate(username, password, authResponse)
			else:
				connectDialog.setText('Connection failed.')
				
		def authResponse(resp):
			if (resp == 0):
				connectDialog.setText('Authentication failed.')
			elif (resp == 1):
				connectDialog.setText('You are already connected.')
			elif (resp == 2):
				connectDialog.setText('Incorrect password.')
			elif (resp == 3):
				connectDialog.setText('Authenticated. You are connected.')
				self.updateGameList()
				
		#def cancel():
		#	print('cancel')
		#	gcli.clientconnection.disconnect()
		#	gui.remove(connectDialog)
		#	del(connectDialog)
			
		print('connecting...')
		
		# Get the values from the form
		server   = self.i_server.getText()
		username = self.i_username.getText()
		password = self.i_password.getText()
		port     = self.i_port.getText()
		
		# If everything is ok attempt to connect and use connectDialog to show the status
		if (server!='' and username!='' and password!='' and port!=''):
			gcli.clientconnection.setAddress(server)
			connectDialog = Dialog('Connecting', text='connecting to server %s'%server, pos=Vec2(250,20))
			gui.add(connectDialog)
			gcli.clientconnection.connect(server, int(port), 3000, connectionResponse)
		else:
			print('You did not fill in the all the values')
			
	def joinGame(self, button=None, key=None, mouse=None):
		
		def joinResponse(resp):
			if (resp == 0):
				gui.add(Alert('Oops!', text='No such game', pos=Vec2(250,20)))
			if (resp == 1):
				gui.add(Alert('Oops!', text='Game full', pos=Vec2(250,20)))
			else:
				self.prnt.startGame(gcli.game)
				
		def downloadResponse(resp):
			if resp:
				gcli.reloadMaps()
				gcli.clientconnection.joinGame(g.id, joinResponse)
				
		# Get the selected game
		if len(self.l_games.selected) > 0:
			selectedGame = self.l_games.selected[0]
		else:
			gui.add(Alert('Oops!', text='No game selected', pos=Vec2(250,20)))
			return
		
		# Find the selected game in the gameList and try to join it
		for g in self.prnt.gameList:
			if g.description == selectedGame:
				# Set game data
				gcli.game = g
				# Check if we have the map for the game
				if g.mapFileName not in gcli.availableMaps.keys():
					print('We dont have the map %s, trying to download it'%g.mapFileName)
					gcli.clientconnection.downloadMap(g.mapFileName, downloadResponse)
				else:
					gcli.clientconnection.joinGame(g.id, joinResponse)
		
class CreateGameDialog(Dialog):
	''' Create server dialog.'''
	def __init__(self, prnt, okFunc=None, cancelFunc=None):
		Dialog.__init__(self, title='Create Game', text='', pos=Vec2(250,20), size=Vec2(270,200), okFunc=okFunc, cancelFunc=cancelFunc)
		
		self.prnt = prnt
		
		# Draw controls
		self.l_status = Lable('', pos=Vec2(10,100))
		self.add(self.l_status)
		self.add(Lable('Max Players:',pos=Vec2(10,60)))
		self.i_maxplayers = Input('3',
				pos=Vec2(90,60),
				size=Vec2(20,20))
		self.add(self.i_maxplayers)
		self.add(Lable('Map',pos=Vec2(10,40)))
		self.d_map = DropDown(gcli.availableMaps.values(),
				gcli.availableMaps.values()[0],
				pos=Vec2(90,40),
				size=Vec2(100,20))
		self.add(self.d_map)
		self.add(Lable('Game Name:',pos=Vec2(10,20)))
		self.i_name = Input('New Game', pos=Vec2(90,20))
		self.add(self.i_name)
		
class OptionForm(Form):
	''' Options menu.'''
	def __init__(self,  prnt):
		Form.__init__(self,'Settings',pos=prnt.menupos, size=prnt.menusize)
		self.prnt = prnt
		
		# Dont show close or sizer button and disable drag.
		self.x.node.hide()
		self.sizer.node.hide()
		self.things[0].onClick=lambda b,k,m : None
		
		# Draw controls	
		self.c_fullscreen = Check('Fullscreen',pos=Vec2(10,50))
		if gcli.gst.fullscreen == 'True':
			self.c_fullscreen.onClick(None, None, None)
		self.add(self.c_fullscreen);
		
		self.c_fpsmeter = Check('FPS Meter',pos=Vec2(10,75))
		if gcli.gst.showFPS == 'True':
			self.c_fpsmeter.onClick(None, None, None)
		self.add(self.c_fpsmeter);
		
		self.i_antiAlias = Input(gcli.gst.antiAlias,pos=Vec2(10,100),size=Vec2(20,20))
		self.add(self.i_antiAlias);
		self.add(Lable('AA (1,2,4,8,16)',pos=Vec2(40,100)))
		
		self.i_alphaBits = Input(gcli.gst.alphaBits,pos=Vec2(10,125),size=Vec2(20,20))
		self.add(self.i_alphaBits);
		self.add(Lable('Alphabits (4,8,16,32)',pos=Vec2(40,125)))
		
		self.i_colorDepth = Input(gcli.gst.colorDepth,pos=Vec2(10,150),size=Vec2(20,20))
		self.add(self.i_colorDepth);
		self.add(Lable('Colordepth (4,8,16,32)',pos=Vec2(40,150)))
		
		self.c_bloom = Check('Bloom',pos=Vec2(10,175))
		if gcli.gst.useBloom == 'True':
			self.c_bloom.onClick(None, None, None)
		self.add(self.c_bloom);
		
		self.c_fog = Check('Fog',pos=Vec2(10,200))
		if gcli.gst.useFog == 'True':
			self.c_fog.onClick(None, None, None)
		self.add(self.c_fog);
		
		self.add(Button('OK',pos=Vec2(40,280), onClick=self.ok))
		self.add(Button('Cancel',pos=Vec2(150,280), onClick=self.prnt.showMain))
		
		# This needs to be done last so the dropdowns show over other widgets
		self.add(Lable('Resolution:',pos=Vec2(10,25)))
		options = ['640x480 (4:3)',
			'800x600 (4:3)',
			'1024x768 (4:3)', 
			'1280x960 (4:3)', 
			'1400x1050 (4:3)', 
			'1600x1200 (4:3)', 
			'1280x1024 (5:4)', 
			'1280x800 (8:5)', 
			'1440x900 (8:5)', 
			'1680x1050 (8:5)', 
			'1920x1200 (8:5)', 
			'854x480 (16:9)', 
			'1280x720 (16:9)', 
			'1920x1080 (16:9)']
		self.d_resolution = DropDown(options, gcli.gst.resolution, pos=Vec2(75,25), size=Vec2(100,20))
		self.add(self.d_resolution)
		
	def ok(self,button,key,mouse):
		# save settings
		gcli.gst.resolution=  self.d_resolution.getOption()
		if self.c_fullscreen.value:
			gcli.gst.fullscreen =  'True'
		else:
			gcli.gst.fullscreen = 'False'
		if self.c_fpsmeter.value:
			gcli.gst.showFPS = 'True'
		else:
			gcli.gst.showFPS = 'False'
		gcli.gst.antiAlias  = self.i_antiAlias.getText()
		gcli.gst.alphaBits  = self.i_alphaBits.getText()
		gcli.gst.colorDepth = self.i_colorDepth.getText()
		if self.c_bloom.value:
			gcli.gst.useBloom = 'True'
		else:
			gcli.gst.useBloom = 'False'
		if self.c_fog.value:
			gcli.gst.useFog   = 'True'
		else:
			gcli.gst.useFog   = 'False'
		gcli.gst.saveSettings()
		self.prnt.showMain(button,key,mouse)
		
class PlayerForm(Form):
	def __init__(self, prnt):
		Form.__init__(self,'Player Setup',pos=prnt.menupos, size=prnt.menusize)
		self.prnt = prnt
		
		# Dont show close or sizer button and disable drag.
		self.x.node.hide()
		self.sizer.node.hide()
		self.things[0].onClick=lambda b,k,m : None
		
		# Draw controls
		self.add(Lable('Nothing here yet. Click OK or Cancel to go',pos=Vec2(60,50)))
		self.add(Lable('back to the main menu',pos=Vec2(60,70)))
		self.add(Button('OK',pos=Vec2(40,280), onClick=self.prnt.showMain))
		self.add(Button('Cancel',pos=Vec2(150,280), onClick=self.prnt.showMain))

class CreditsForm(Form):
	def __init__(self, prnt):
		Form.__init__(self,'Credits',pos=prnt.menupos, size=prnt.menusize)
		self.prnt = prnt
		
		# Dont show close or sizer button and disable drag.
		self.x.node.hide()
		self.sizer.node.hide()
		self.things[0].onClick=lambda b,k,m : None
		
		self.add(Lable('Nothing here yet. Click OK or Cancel to go',pos=Vec2(60,50)))
		self.add(Lable('back to the main menu',pos=Vec2(60,70)))
		self.add(Button('OK',pos=Vec2(40,280), onClick=self.prnt.showMain))
		self.add(Button('Cancel',pos=Vec2(150,280), onClick=self.prnt.showMain))
