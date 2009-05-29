''' GameServer.py
	Author:			Chad Rempp
	Date:			2009/05/07
	Purpose:		The game server handles sharing games between connected
					clients and passes messages.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			TODO - Document the communication protocol (and make it
							consistent).
						 - Make the PSGServer a singleton.
						 - Add a clean command to clear abandoned connections
						 - Add a periodic ping to check dead connections
'''

# Python imports
import sys, hashlib, platform, time, os
from datetime import datetime

# Panda imports
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-type none")
loadPrcFileData('', 'client-sleep 0.01')
import direct.directbase.DirectStart
from direct.task import Task
from pandac.PandaModules import QueuedConnectionManager
from pandac.PandaModules import QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader
from pandac.PandaModules import ConnectionWriter
from pandac.PandaModules import PointerToConnection
from pandac.PandaModules import NetAddress
from pandac.PandaModules import NetDatagram
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

# PSG imports


OS_TYPE = platform.system()
if (OS_TYPE == 'Linux'):
	print("trying Linux")
	import select
elif (OS_TYPE == 'Windows'):
	print("trying win")
	import msvcrt
else:
	print('Operating system not supported, exiting')
	sys.exit()

PORT    = 9099 #TCP/IP port to listen on
BACKLOG = 100  #If we ignore this many connection attempts, something is wrong!
MAX_GAMES = 50

MSG_NONE           = 0
MSG_AUTH_REQ       = 1
MSG_AUTH_RES       = 2 # 0=Auth denied, 1=Already connected, 2=Auth Granted
MSG_MAPLIST_REQ    = 3
MSG_MAPLIST_RES    = 4
MSG_GAMELIST_REQ   = 5
MSG_GAMELIST_RES   = 6
MSG_NEWGAME_REQ    = 7
MSG_NEWGAME_RES    = 8 # 0=Failed, 1=Succeeded
MSG_JOINGAME_REQ   = 9
MSG_JOINGAME_RES   = 10
MSG_CHAT_REQ       = 27
MSG_CHAT_RES       = 28
MSG_UNITMOVE_REQ   = 29
MSG_UNITMOVE_RES   = 30
MSG_UNITATTACK_REQ = 31
MSG_UNITATTACK_RES = 32
MSG_UNITINFO_REQ   = 33
MSG_UNITINFO_RES   = 34
MSG_ENDTURN_REQ    = 35
MSG_ENDTURN_RES    = 36
MSG_PING_REQ       = 48
MSG_PING_RES       = 49
MSG_DISCONNECT_REQ = 50
MSG_DISCONNECT_RES = 51

GAME_IDS = range(MAX_GAMES)
def getGameID():
	''' This helper function returns the first available game ID. If none
		are available it returns -1.'''
	if (len(GAME_IDS) > 0):
		id = GAME_IDS[0]
		GAME_IDS.remove(id)
		return id
	else: return -1
	
def releaseGameID(id):
	''' This helper function inserts a game ID in the the list of available
		IDs. If inserting the ID would result in there being more than MAX_GAMES
		it returns -1.'''
	if (len(GAME_IDS) < MAX_GAMES):
		GAME_IDS.append(id)
		GAME_IDS.sort()
	else: return -1
	
MAPLIST = []
def reloadMaps():
	''' A helper function to create a dictionary of available map files. The
		dictionary format is {filename:md5sum}.'''
	global MAPLIST
	MAPLIST = []
	# List all map files
	for f in os.listdir('data/maps'):
		if (os.path.splitext(f)[1] == '.map'):
			check = hashlib.md5(file('data/maps/'+f,'rb').read()).hexdigest()
			MAPLIST.append({f:check})
			
def getMap(filename):
	for m in MAPLIST:
		if filename in m.keys():
			return m
	return None
		

#_GAME_CLASS___________________________________________________________________
class ServerGame:
	''' The game class stores all information for active games. It also handles
		passing messages between connected clients.'''
	id         = 0
	name       = 'New Game'
	players    = [] # List of Clients
	maxPlayers = 2
	map        = None #{name: md5sum}
	mapName    = 'None'
	turnNumber = 0
	startTime  = None
	
	def __init__(self, name, maxplayers, mapname):
		''' Creates a new game.
			id (Int): the unique id of this game
			name (String): the name of this game
			maxplayers (Int): maximum players allowed to participate
			map (String): the file name of the map being used'''
		self.id         = getGameID()
		if (self.id < 0):
			print('Error getting a game ID!')
		self.name       = name
		self.maxPlayers = maxplayers
		self.startTime  = int(time.time())
		self.mapName    = mapname
		self.setMap(mapname)

	def setMap(self, mapname):
		if (mapname != None and mapname != ''):
			self.mapFile    = mapname.replace(' ','')+'.map'
			self.mapCheck   = hashlib.md5(file('data/maps/'+self.mapFile,'rb').read()).hexdigest()
			
	def addPlayer(self, player):
		''' Adds a player to the game.
			player (User): the user to be added to the game'''
		self.players.append(player)
		
	def __del__(self):
		releaseGameID(self.id)

#_USER_CLASS___________________________________________________________________
class User:
	''' The User class stores all relevant information for a user. It has the
	    collection of stats for the user and the current state of the user
	    (connected, time online, ...).
	'''
	username = ''
	password = ''
	connected = False
	connectedAddress = None
	connectedTime = None
	connectHistory = []
	
	def __init__(self, usr, passwd):
		''' Creates a new user.
			usr (String): the user name
			passwd (String): the plain text password which is then encrypted
				and stored.'''
		self.username = usr
		h = hashlib.sha256()
		h.update(passwd)
		self.password = h.hexdigest()
		
	def authorize(self, passwd, client):
		''' Compares encrypted passwords to determine authorization, if
		    authorized we set the connection state for this user.
		    passwd (String): an encrypted password
		    client (Client): the client the user is connecting from.'''
		if (passwd == self.password):
			self.connect(client)
	
	def connect(self, client):
		''' Set up the users connection state.
			client (Client): the client the user is connecting from,'''
		self.connected = True
		self.connectedTime = datetime.now()
		self.connectedClient = client
		self.connectedAddress = client
		self.connectHistory.append({client:self.connectedTime})
	
	def disconnect(self):
		''' Reset the users connection state.'''
		self.connected = False
		self.connectedTime = None

#_PSGSERVER____________________________________________________________________
class PSGServer():
	''' The main server that listens for connections and manages active games.
		This also runs the console which can interact with the server.'''
	users = [User('chad','password1'),
		     User('josh','password2'),
		     User('james','password3')]
	# Clients is a dict of the form {Connection: User}
	clients = {}
	# games is a list of active games
	games = []
	_haveCommand = True
	_command     = ''
	_commandTok  = []

	def __init__(self):
		''' Initialize the server.'''
		print('Starting PSG Server ...')
		self._cManager  = QueuedConnectionManager()
		self._cListener = QueuedConnectionListener(self._cManager, 0)
		self._cReader   = QueuedConnectionReader(self._cManager, 0)
		self._cWriter   = ConnectionWriter(self._cManager,0)
		
		#TODO - Load user file (DB)
		
		#Load maps
		reloadMaps()
		
		self._tcpSocket = self._cManager.openTCPServerRendezvous(PORT,BACKLOG)
		self._cListener.addConnection(self._tcpSocket)
		
		taskMgr.add(self.__listenTask, 'serverListenTask', -40)
		taskMgr.add(self.__readTask, 'serverReadTask', -39)
		if OS_TYPE == 'Linux':
			taskMgr.add(self.__consoleTask_u, 'consoleTask', -38)
		elif OS_TYPE == 'Windows':
			taskMgr.add(self.__consoleTask_w, 'consoleTask', -38)
		
		# Build some test games
		for i in range(4):
			g = ServerGame('Test game - %d'%i, i, '')
			self.games.append(g)
			
		print('Server initialized')
		
	def __listenTask(self, Task):
		''' This task listens for connections. When a connection is made it
			adds the connection to the clients list and begins listening to
			that connection.'''
		if self._cListener.newConnectionAvailable():
			rendezvous = PointerToConnection()
			netAddress = NetAddress()
			newConnection = PointerToConnection()
			
			if self._cListener.getNewConnection(rendezvous,netAddress,newConnection):
				newConnection = newConnection.p()
				self.clients[newConnection] = None
				self._cReader.addConnection(newConnection)     # Begin reading connection
				self.__printNotice('Connection from %s'%netAddress.getIpString())
		return Task.cont
	
	def __readTask(self, Task):
		''' This task listens for any messages coming in over any connections.
			If we get a connection passes it to the datagram handler.'''
		if self._cReader.dataAvailable():
			datagram=NetDatagram()
			if self._cReader.getData(datagram):
				data = PyDatagramIterator(datagram)
				msgID = data.getUint16()
			else:
				data = None
				msgID = MSG_NONE
		else:
			datagram = None
			data = None
			msgID = MSG_NONE
		if msgID is not MSG_NONE:
			self.__handleDatagram(data, msgID, datagram.getConnection())
		return Task.cont
	
	def __handleDatagram(self, data, msgID, client):
		''' This handles incoming messages. It can run the appropriate handler
			from the server or pass it to the relevant game to deal with.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		self.__printNotice('%s: Recieved msg: %d'%(client.getAddress().getIpString(),msgID))
		if (msgID == MSG_AUTH_REQ):
			self.__handleAuth(data, msgID, client)
		elif (msgID == MSG_GAMELIST_REQ):
			print('SENDING GAMELIST RES')
			self.__handleGameList(data, msgID, client)
		elif (msgID == MSG_NEWGAME_REQ):
			print('SENDING NEWGAME RES')
			self.__handleNewGame(data, msgID, client)
		elif (msgID == MSG_JOINGAME_REQ):
			print('SENDING JOINGAME RES')
			self.__handleJoinGame(data, msgID, client)
		elif (msgID == MSG_DISCONNECT_REQ):
			print('SENDING DISCONNECT RES')
			self.__handleDisconnect(data, msgID, client)
		else:
			self.__printNotice('%s: Unkown MSG_ID: %d'%(client.getAddress().getIpString(),msgID))
			print(data)
	
	def __handleAuth(self, data, msgID, client):
		''' Try to authorize the connecting user, send the result.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		username = data.getString()
		password = data.getString()
		auth = 0
		
		for u in self.users:
			if u.username == username:
				if u.connected:
					auth = 1
					self.__printNotice('%s: User %s already connected'%(client.getAddress().getIpString(),username))
				elif u.password == password:
					auth = 2
					for c in self.clients.keys():
						if c == client:
							self.clients[c] = u
					u.connect(client)
		
		self.__printNotice('%s: User %s tried to connect with pass %s. Gave %d.' %(client.getAddress().getIpString(),username,password,auth))
		pkg = NetDatagram()
		pkg.addUint16(MSG_AUTH_RES)
		pkg.addUint32(auth)
		self._cWriter.send(pkg, client)
	
	def __handleGameList(self, data, msgID, client):
		''' Assemble a list of active games and send it to the requesting client.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		self.__printNotice('%s: Request for game list.' %(client.getAddress().getIpString()))
		pkg = NetDatagram()
		pkg.addUint16(MSG_GAMELIST_RES)
		pkg.addString('SOT') # Start Of Transmission
		for i,g in enumerate(self.games):
			pkg.addUint32(g.id)
			pkg.addString(g.name)
			pkg.addUint32(g.maxPlayers)
			pkg.addString(g.mapName)
			pkg.addUint32(g.startTime)
			pkg.addUint32(g.turnNumber)
			if i < len(self.games)-1:
				pkg.addString('T') # Still tranmitting
		pkg.addString('EOT') # End Of Transmission
		self._cWriter.send(pkg, client)
		
	def __handleNewGame(self, data, msgID, client):
		''' Create a new game and respond with success or failure.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		name       = data.getString()
		map        = data.getString()
		maxPlayers = data.getUint32()
		self.__printNotice('%s: Request for new game: %s, %s, %d.' %(client.getAddress().getIpString(),name,map,maxPlayers))
		
		newGame = ServerGame(name, maxPlayers, map)
		
		pkg = NetDatagram()
		pkg.addUint16(MSG_NEWGAME_RES)
		if newGame:
			#print('newgame success')
			self.games.append(newGame)
			pkg.addUint32(1)
		else:
			#print('newgame failed')
			pkg.addUint32(0)
		self._cWriter.send(pkg, client)
		
	def __handleJoinGame(self, data, msgID, client):
		''' Add client to the requested game.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		id = data.getUint32()
		resp = 0
		
		# Get the game
		game = None
		for g in self.games:
			if g.id == id:
				game = g
		
		pkg = NetDatagram()
		pkg.addUint16(MSG_JOINGAME_RES)
		
		if game == None:
			print('No such game')
			resp = 0
		elif len(game.players) >= game.maxPlayers:
			print('Game full')
			resp = 1
		else:
			game.addPlayer(client)
			print('OK')
			resp = 2
			
		pkg.addUint32(resp)
		self._cWriter.send(pkg, client)
		self.__printNotice('%s: Request to join game id %d, gave %d.'%(client.getAddress().getIpString(),id,resp))
		
	def __handleDisconnect(self, data, msgID, client):
		''' Disconnect and send confirmation to the client.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		# Create a response
		pkg = NetDatagram()
		pkg.addUint16(MSG_DISCONNECT_RES)
		self._cWriter.send(pkg, client)
		
		# If user is logged in disconnect
		user = self.clients[client]
		if user:
				user.disconnect()
		
		# Delete client from list
		del self.clients[client]
		
		#print('disconnected client %s'%client.getAddress().getIpString())
		
	def __consoleTask_u(self, Task):
		'''This task accepts commands for the server in a Unix environment.
		   We use select as a non-blocking input.'''
		if self._haveCommand:
			self.__handleCommand()
			#self._commandTok = self._command.split()
			#print(self._commandTok)
			print("psgconsole: "),
			sys.stdout.flush()
			self._command = []
			self._haveCommand = False
		r,w,x = select.select([sys.stdin.fileno()],[],[],0)
		if (len(r) != 0):
			cmd = sys.stdin.readline()
			self._command = cmd[0:len(self._command)-1]
			self._commandTok = cmd.split()
			self._haveCommand = True
		return Task.cont
	
	def __consoleTask_w(self, Task):
		'''This task accepts commands for the server in a Windows environment.
		   We use select as a non-blocking input.'''
		if msvcrt.kbhit():
			c = msvcrt.getche()
			if (c == '\r'): self._haveCommand = True
			elif (c=='\b'):
				# TODO - Also clear the onscreen buffer of the character
				self._command = self._command[0:len(self._command)-1]
			else: self._command += c
		if self._haveCommand:
			cmd = self._command[0:len(self._command)-1]
			print(cmd)
			self._commandTok = cmd.split()
			print("\bpsg: " + self._command)
			self.__handleCommand()
			print("psg: "),
			self._command = []
			self._haveCommand = False
		return Task.cont
	
	def __handleCommand(self):
		''' Call the appropriate handler for the current console command.
		exit
		lsconn
		lsusers
		lsgames
		kill		-c# -u# -g#
		reload		-m (maps)'''
		if (len(self._commandTok) > 0):
			if self._commandTok[0] == 'exit':
				self.__quit()
			elif self._commandTok[0] == 'lsconn':
				self.__lsConnections()
			elif self._commandTok[0] == 'lsusers':
				self.__lsUsers()
			elif self._commandTok[0] == 'lsgames':
				self.__lsGames()
			else: # Unknown command
				self.__printLine('Unknown command, I understand these:')
				self.__printLine('lsconn      lsusers     lsgames')
		
	def __lsConnections(self):
		''' Print all current connections'''
		keys = self.clients.keys()
		self.__printLine('\b_ADDR__________|_USER__________|_GAME__________')
		if (len(keys) == 0):
			self.__printLine("No connections")
		else:
			for k in keys:
				addr = k.getAddress().getIpString()
				if self.clients[k] != None:
					user = self.clients[k].username
				else:
					user = 'NONE'
				game = 'NONE'
				self.__printLine("%s|%s|%s"%(addr.ljust(15),user.ljust(15),game.ljust(15)))
				
	def __lsUsers(self):
		''' Print all users currently signed in'''
		self.__printLine('\b_USER__________|_ADDR__________|_GAME__________')
		if (len(self.users) == 0):
			self.__printLine("No users")
		else:
			for u in self.users:
				if u.connected:
					user = u.username
					game = 'NONE'
					addr = '0.0.0.0'
					for c in self.clients.keys():
						if (self.clients[c].username == user):
							addr = c.getAddress().getIpString()
					self.__printLine("%s|%s|%s"%(user.ljust(15),addr.ljust(15),game.ljust(15)))
					
	def __lsGames(self):
		''' Print all active games.'''
		self.__printLine('\b_ID_|_NAME__________|_MAP___________|_MX_PL_|_TURN_|_RUNTIME_')
		if (len(self.games) == 0):
			self.__printLine("No games")
		else:
			for g in self.games:
				runtime = (int(time.time()) - g.startTime) # Divide by 60 for minutes
				self.__printLine("%s|%s|%s|%s|%s|%s"%(str(g.id).ljust(4),
							g.name.ljust(15),g.mapName.ljust(15),
							str(g.maxPlayers).ljust(7),
							str(g.turnNumber).ljust(6),str(runtime)))
				
	def __quit(self):
		''' Clean up and shutdown. Tell all connected clients that we are
			shutting down, close connections and quit.'''
		print('Shutting down server ...')
		
		# Send disconnect to all clients
		pkg = NetDatagram()
		pkg.addUint16(MSG_DISCONNECT_REQ)
		for c in self.clients.keys():
			self._cWriter.send(pkg, c)
		self._cManager.closeConnection(self._tcpSocket)
		print('Server done')
		sys.exit()
		
	def __printNotice(self, msg):
		''' Print notices to stdout.
			TODO - add in log file option.'''
		print('NOTICE: %s'%msg)
		sys.stdout.flush()
	
	def __printLine(self, msg):
		''' This is the print function for the console commands.'''
		outMsg = msg
		if OS_TYPE == 'Linux':
			sys.stdout.flush()
			print(outMsg)
			sys.stdout.flush()
		elif OS_TYPE == 'Windows':
			print(outMsg)
			
server = PSGServer()

run()
