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
						 - Add command to turn on/off notices
'''

# Python imports
from datetime import datetime
import hashlib
import os
import platform
import sys
import time

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
from Protocol import *
import Game
import Map

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

PORT       = 9099 #TCP/IP port to listen on
BACKLOG    = 100  #If we ignore this many connection attempts, something is wrong!
PING_DELAY = 60 # Seconds between pinging connections
PING_TIMEOUT = 10 # Seconds to wait for a ping response

class User:
	''' The User class stores all relevant information for a user. It has the
		collection of stats for the user and the current state of the user
		(connected, time online, ...).
		TODO - Implement connection history
	'''
	username         = ''
	password         = ''
	connected        = False
	connectedAddress = None
	connectedTime    = None
	connectHistory   = []
	connectedClient  = None
	connectedAddress = ''
	
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
		self.connectedAddress = client.getAddress().getIpString()
		self.connectHistory.append({client:self.connectedTime})
	
	def disconnect(self):
		''' Reset the users connection state.'''
		self.connected = False
		self.connectedTime = None

class PSGServer():
	''' The main server that listens for connections and manages active games.
		This also runs the console which can interact with the server.'''
		
	# registeredUsers is a list of User objects of registered users
	registeredUsers = []
	# connectedUsers is a list of User objects of currently connected users
	connectedUsers  = []
	# connections is a list of Connection objects
	connections =[]
	# Connections that have not responded to their keepalive request.
	# A dictionary of the form (Connection, pingtime)
	pingNonResponders = {}
	# games is a list of active ServerGame objects
	games = []
	# The following are for the console
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
		self.registeredUsers =[User('chad','password1'),
							   User('josh','password2'),
							   User('james','password3')]
		
		# Open socket
		self._tcpSocket = self._cManager.openTCPServerRendezvous(PORT,BACKLOG)
		self._cListener.addConnection(self._tcpSocket)
		
		# Setup system tasks
		taskMgr.add(self.__listenTask, 'serverListenTask', -40)
		taskMgr.add(self.__readTask, 'serverReadTask', -39)
		taskMgr.doMethodLater(PING_DELAY, self.__pingTask, 'serverPingTask', sort=-41)
		taskMgr.doMethodLater(1, self.__checkPingRespTask, 'serverCheckPingRespTask', sort=-10)
		
		if OS_TYPE == 'Linux':
			taskMgr.add(self.__consoleTask_u, 'consoleTask', -38)
		elif OS_TYPE == 'Windows':
			taskMgr.add(self.__consoleTask_w, 'consoleTask', -38)
			
		print('Server initialized')
	
	#_Communtication_Methods___________________________________________________	
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
				if newConnection not in self.connections:
					self.connections.append(newConnection)
					self._cReader.addConnection(newConnection)     # Begin reading connection
					self.__printNotice('Connection from %s'%netAddress.getIpString())
				else:
					self.__printNotice('%s: already connected'%(newConnection.getAddress().getIpString()))
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
	
	def __pingTask(self, Task):
		''' Ping all clients every PING_DELAY seconds to check for those who
			have dropped their connection.'''
		print('Pinging: '),
		
		for c in self.connections:
			# Don't ping connections we're still waiting on
			if c not in self.pingNonResponders.keys():
				print('%s '%c.getAddress().getIpString()),
				self.pingNonResponders[c] = int(time.time())
				pkg = NetDatagram()
				pkg.addUint16(MSG_PING_REQ)
				self._cWriter.send(pkg, c)
		
		print('')
		# Add task back into the taskmanager
		taskMgr.doMethodLater(PING_DELAY, self.__pingTask, 'serverPingTask', sort=-41)
		
	def __checkPingRespTask(self, Task):
		''' Run through the list of connections that haven't responded to their
			ping yet and disconnect them if has been more than PING_TIMEOUT
			seconds.'''
		
		#print('Checking ping responses: '),
		for c in self.pingNonResponders.keys():
			#print('%s '%c.getAddress().getIpString()),
			now = int(time.time())
			pingTime = self.pingNonResponders[c]
			if ((now - pingTime) > PING_TIMEOUT):
				#print('disconnecting '),
				self.__handleDisconnect(None, None, c)
		#print('')
		# Add task back into the taskmanager
		taskMgr.doMethodLater(1, self.__checkPingRespTask, 'serverCheckPingRespTask', sort=-10)
	
	def __handleDatagram(self, data, msgID, client):
		''' This handles incoming messages. It can run the appropriate handler
			from the server or pass it to the relevant game to deal with.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		self.__printNotice('%s: Recieved msg: %d'%(client.getAddress().getIpString(),msgID))
		# System messages
		if (msgID == MSG_PING_REQ):
			self.__printNotice('Notice: MSG_PING_REQ')
			self.__handlePingReq(data, msgID, client)
		elif (msgID == MSG_PING_RES):
			self.__printNotice('Notice: MSG_PING_RES')
			self.__handlePingRes(data, msgID, client)
		elif (msgID == MSG_DISCONNECT_REQ):
			self.__printNotice('Notice: MSG_DISCONNECT_REQ')
			self.__handleDisconnect(data, msgID, client)
		# Pre-game server messages
		elif (msgID == MSG_AUTH_REQ):
			self.__printNotice('Notice: MSG_AUTH_REQ')
			self.__handleAuth(data, msgID, client)
		elif (msgID == MSG_MAPLIST_REQ):
			self.__printNotice('Notice: MSG_MAPLIST_REQ')
			#self.__handleMapList(data, msgID, client)
		elif (msgID == MSG_GAMELIST_REQ):
			self.__printNotice('Notice: MSG_GAMELIST_REQ')
			self.__handleGameList(data, msgID, client)
		elif (msgID == MSG_NEWGAME_REQ):
			self.__printNotice('Notice: MSG_NEWGAME_REQ')
			self.__handleNewGame(data, msgID, client)
		elif (msgID == MSG_JOINGAME_REQ):
			self.__printNotice('Notice: MSG_JOINGAME_REQ')
			self.__handleJoinGame(data, msgID, client)
		# In-game server messages
		elif (msgID == MSG_CHAT_SEND):
			self.__printNotice('Notice: MSG_CHAT_REQ')
			self.__handleChat(data, msgID, client)
		elif (msgID == MSG_UNITMOVE_SEND):
			self.__printNotice('Notice: MSG_UNITMOVE_REQ')
			self.__handleUnitMove(data, msgID, client)
		elif (msgID == MSG_UNITATTACK_SEND):
			self.__printNotice('Notice: MSG_UNITATTACK_REQ')
			self.__handleUnitAttack(data, msgID, client)
		elif (msgID == MSG_UNITINFO_SEND):
			self.__printNotice('Notice: MSG_UNITINFO_REQ')
			self.__handleUnitInfo(data, msgID, client)
		elif (msgID == MSG_ENDTURN_SEND):
			self.__printNotice('Notice: MSG_ENDTURN_REQ')
			self.__handleEndTurn(data, msgID, client)
		else:
			self.__printNotice('%s: Unkown MSG_ID: %d'%(client.getAddress().getIpString(),msgID))
			print(data)
	
	def __handlePingReq(self, data, msgID, client):
		''' Respond to a ping request.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_PING_RES)
		self._cWriter.send(pkg, client)
		
		self.__printNotice('%s: Ping request'%(client.getAddress().getIpString()))
		
	def __handlePingRes(self, data, msgID, client):
		''' Handle an incoming ping response.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
			
		# Client responded so remove from non-responder list
		del(self.pingNonResponders[client])
		self.__printNotice('%s: Ping response'%(client.getAddress().getIpString()))
	
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
		username = ''
		for u in self.connectedUsers:
			if (u.connectedClient == client):
				username = u.username
				u.disconnect()
				self.connectedUsers.remove(u)
		
		# Delete client from list
		if client in self.connections:
			self.connections.remove(client)
		
		self.__printNotice('%s: Disconnected user %s'%(client.getAddress().getIpString(),username))
	
	def __handleAuth(self, data, msgID, client):
		''' Try to authorize the connecting user, send the result.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		
		# Unpack message data
		username = data.getString()
		password = data.getString()
		auth = 0
		
		# Look for the username in the list of registered users
		for u in self.registeredUsers:
			if u.username == username:
				if u.connected:
					auth = 1
					self.__printNotice('%s: User %s already connected'%(client.getAddress().getIpString(),username))
					break
				elif u.password != password:
					auth = 2
					self.__printNotice('%s: User %s gave invalid password'%(client.getAddress().getIpString(),username))
					break
				else:
					auth = 3
					u.connect(client)
					self.connectedUsers.append(u)
					self.__printNotice('%s: User %s connected with pass %s' %(client.getAddress().getIpString(),username,password))
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_AUTH_RES)
		pkg.addUint32(auth)
		self._cWriter.send(pkg, client)
	
	def __handleMapList(self, data, msgID, client):
		''' Assemble a list of available maps and send it to the requesting client.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		
		# Assemble a list with entries in the form (filename,mapname,md5sum)
		mapFileList = Map.getMapFiles()
		responseList = []
		for f in mapFileList:
			fh = open(Map.MAP_PATH + f,' rb')
			mapObj = cPickle.load(fh)
			responseList.append((mapObj.name, f, Map.getMapMD5(f)))
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_MAPLIST_RES)
		pkg.addString('SOT') # Start Of Transmission
		for i, (n,f,c) in enumerate(responseList):
			pkg.addString(n)
			pkg.addString(f)
			pkg.addString(c)
			if i < len(responseList)-1:
				pkg.addString('T') # Still tranmitting
		pkg.addString('EOT') # End Of Transmission
		self._cWriter.send(pkg, client)
		
		self.__printNotice('%s: Request for map list.' %(client.getAddress().getIpString()))
	
	def __handleGameList(self, data, msgID, client):
		''' Assemble a list of active games and send it to the requesting client.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_GAMELIST_RES)
		if (len(self.games) == 0):
			pkg.addString('EOT') # Nothing to transmit
		else:
			pkg.addString('SOT') # Start Of Transmission
			for i,g in enumerate(self.games):
				pkg.addUint32(g.id)
				pkg.addString(g.name)
				pkg.addUint32(g.maxPlayers)
				pkg.addString(g.mapName)
				pkg.addString(g.mapFileName)
				pkg.addUint32(g.startTime)
				pkg.addUint32(g.turnNumber)
				if i < len(self.games)-1:
					pkg.addString('T') # Still tranmitting
			pkg.addString('EOT') # End Of Transmission
		self._cWriter.send(pkg, client)
		
		self.__printNotice('%s: Request for game list.' %(client.getAddress().getIpString()))
		
	def __handleNewGame(self, data, msgID, client):
		''' Create a new game and respond with success or failure.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		# Unpack message data
		gameName    = data.getString()
		mapName     = data.getString()
		mapFileName = data.getString()
		maxPlayers  = data.getUint32()
		
		# Create the game
		newGame = Game.ServerGame(gameName, maxPlayers, mapName, mapFileName)
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_NEWGAME_RES)
		if newGame:
			self.games.append(newGame)
			pkg.addUint32(newGame.id)
		else:
			pkg.addUint32(0)
		self._cWriter.send(pkg, client)
		
		self.__printNotice('%s: Request for new game: %s, %s, %d.' %(client.getAddress().getIpString(),gameName,mapFileName,maxPlayers))
		
	def __handleJoinGame(self, data, msgID, client):
		''' Add client to the requested game.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		# Unpack message data
		id = data.getUint32()
		resp = 0
		
		# Find the game
		game = None
		for g in self.games:
			if g.id == id:
				game = g
		
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
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_JOINGAME_RES)
		pkg.addUint32(resp)
		self._cWriter.send(pkg, client)
		self.__printNotice('%s: Request to join game id %d, gave %d.'%(client.getAddress().getIpString(),id,resp))
		
	def __handleChat(data, msgID, client):
		''' Player chat.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		
	def __handleUnitMove(data, msgID, client):
		''' Unit move.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		self.__printNotice('%s: Unit move request.'%(client.getAddress().getIpString()))
	
	def __handleUnitAttack(data, msgID, client):
		''' Unit attack.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		self.__printNotice('%s: Unit attack request.'%(client.getAddress().getIpString()))
	
	def __handleUnitInfo(data, msgID, client):
		''' Unit information.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		self.__printNotice('%s: Unit information request.'%(client.getAddress().getIpString()))
	
	def __handleEndTurn(data, msgID, client):
		''' End turn.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
			
		self.__printNotice('%s: End turn request.'%(client.getAddress().getIpString()))
	
	#_Console_Methods__________________________________________________________
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
		   We use getch as a non-blocking input.'''
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
		kill		-c# -u# -g#'''
		if (len(self._commandTok) > 0):
			if self._commandTok[0] == 'exit':
				self.__quit()
			elif self._commandTok[0] == 'lsconn':
				self.__lsConnections()
			elif self._commandTok[0] == 'lsusers':
				self.__lsUsers()
			elif self._commandTok[0] == 'lsgames':
				self.__lsGames()
			elif self._commandTok[0] == 'kill':
				self.__kill()
			else: # Unknown command
				self.__printLine('Unknown command, I understand these:')
				self.__printLine('lsconn      lsusers     lsgames')
				self.__printLine('kill')
		
	def __lsConnections(self):
		''' Print all current connections'''
		self.__printLine('\b_ADDR__________|_USER__________|_GAME__________')
		if (len(self.connections) == 0):
			self.__printLine("No connections")
		else:
			for c in self.connections:
				addr = c.getAddress().getIpString()
				user = 'NONE'
				for u in self.connectedUsers:
					if (u.connectedClient == c):
						user = u.username
				game = 'NONE'
				for g in self.games:
					if (u in g.players):
						game = g.name
				self.__printLine("%s|%s|%s"%(addr.ljust(15),user.ljust(15),game.ljust(15)))
				
	def __lsUsers(self):
		''' Print all users currently signed in'''
		self.__printLine('\b_USER__________|_ADDR__________|_GAME__________')
		if (len(self.registeredUsers) == 0):
			self.__printLine("No users")
		else:
			for u in self.registeredUsers:
				user = u.username
				game = ''
				addr = ''
				if u.connected:
					addr = u.connectedClient.getAddress().getIpString()
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
				
	def __kill(self):
		''' Depending on parameters kill a game, connection or user.'''
		
		if (len(self._commandTok) == 2):
			try:
				type = self._commandTok[1][1]
				id   = self._commandTok[1][3:]
				print('%s %s'%(type,id))
			except:
				self.__printLine('USAGE: kill -c=address -u=username -g=id')
			finally:
				if (type=='c'): # Kill client
					foundClient = False
					for c in self.connections:
						if (c.getAddress().getIpString() == id):
							foundClient = True
							self.__handleDisconnect(None, None, client)
					if not foundClient:
						self.__printLine('Did not find client %s'%id)
				elif (type=='u'): # Kill user
					foundUser = False
					for u in self.connectedUsers:
						if (u.username == id):
							foundUser = True
							self.__handleDisconnect(None, None, u.connectedClient)
					if not foundUser:
						self.__printLine('User %s not connected'%id)
				elif (type=='g'): # Kill game
					foundGame = False
					for g in self.games:
						if (g.id == id):
							for u in g.players:
								self.__handleDisconnect(None, None, u.connectedClient)
							self.games.remove(g)
				else:
					self.__printLine('USAGE: kill -c=address -u=username -g=id')
		else:
			self.__printLine('USAGE: kill -c=address -u=username -g=id')
		
	def __quit(self):
		''' Clean up and shutdown. Tell all connected clients that we are
			shutting down, close connections and quit.'''
		print('Shutting down server ...')
		
		# Send disconnect to all clients
		pkg = NetDatagram()
		pkg.addUint16(MSG_DISCONNECT_REQ)
		for c in self.connections:
			self._cWriter.send(pkg, c)
		self._cManager.closeConnection(self._tcpSocket)
		print('Server done')
		sys.exit()
		
	#_Console_Display_Methods__________________________________________________
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
			
# Run the server
server = PSGServer()
run()
