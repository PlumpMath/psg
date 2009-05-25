''' ClientConnection.py
	Author:			Chad Rempp
	Date:			2009/05/09
	Purpose:		The ClientConnection connects to a game server and passes
					messages between the game and the server.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			
	'''

# Python imports
import hashlib, sys, time

# Panda imports
from direct.task import Task
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import ConnectionWriter
from pandac.PandaModules import NetDatagram
from pandac.PandaModules import QueuedConnectionManager
from pandac.PandaModules import QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader

MSG_NONE           = 0
MSG_AUTH_REQ       = 1
MSG_AUTH_RES       = 2 # 0=Auth denied, 1=Already connected, 2=Auth Granted
MSG_MAPLIST_REQ    = 3
MSG_MAPLIST_RES    = 4
MSG_GAMELIST_REQ   = 5
MSG_GAMELIST_RES   = 6
MSG_NEWGAME_REQ    = 7
MSG_NEWGAME_RES    = 8 # 0=Failed, 1=Succeeded
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

class ClientConnection:
	''' This class creates the communication links to a game server and
		presents an interface for communication.'''
	_address        = '127.0.0.1'
	_port           = '9099'
	_timeout        = '3000'
	_callback       = None
	_connected      = False
	_authorized   	= False
	_connectedGame 	= None
	#_availableGames = {}
	_respCallback   = {MSG_AUTH_RES: None,
					   MSG_MAPLIST_RES: None,
					   MSG_GAMELIST_RES: None,
					   MSG_NEWGAME_RES: None,
					   MSG_CHAT_RES: None}
	def __init__(self):
		self._cManager   = QueuedConnectionManager()
		self._cListener  = QueuedConnectionListener(self._cManager, 0)
		self._cReader    = QueuedConnectionReader(self._cManager, 0)
		self._cWriter    = ConnectionWriter(self._cManager,0)
	
	#--ClientConnection Interface-----------------------------------------------
	def authenticate(self, username, password, callback):
		''' Send authentication request. Callback will be called with the
			response.'''
		self.__sendAuthReq(username, password)
		self._respCallback[MSG_AUTH_RES] = callback
	
	def connect(self, address, port, timeout, callback):
		''' Try to connect to the server. If successfull callback is passed 1, else 0.
			address (String): address for the server
			port (Int): port to connect to
			timeout (Int): how long to wait before giving up (milliseconds)'''
		if self._connected:
			print("Already Connected!")
		try:
			print('connecting to %s'%address)
			self._tcpSocket = self._cManager.openTCPClientConnection(address, port, timeout)
			self._cReader.addConnection(self._tcpSocket)  # receive messages from server
			taskMgr.add(self.__readTask,"Poll the connection reader",-40)
			self._connected = 1
		except Exception as e:
			print("Couldn't connect to server: %s"%e)
			self._connected = 0
		callback(self._connected)
		
	def disconnect(self, callback):
		''' Disconnect from the server.
			If successful callback is passed 1, else 0.'''
		if self._connected:
			print('Disconnecting...')
			pkg = NetDatagram()
			pkg.addUint16(MSG_DISCONNECT_REQ)
			self._cWriter.send(pkg, self._tcpSocket)
			self._cManager.closeConnection(self._tcpSocket)
			self._connected = False
			if callback != None: callback(1)
		else:
			print('Can not disconnect, we are not connected.')
			if callback != None: callback(0)
	
	def getAddress(self):
		return self._address
	
	def getCallback(self):
		return self._callback
	
	def getGameList(self, callback):
		''' Sends a request for a list of active games to the server.
			On success callback is passed a dictionary of the form,
			{id: 'descriptive string'}.'''
		self.__sendGameListReq()
		self._respCallback[MSG_GAMELIST_RES] = callback
		
	def getPort(self):
		return self._port
		
	def getTimeout(self):
		return self._timeout
	
	def isConnected(self):
		return self._connected
		
	def joinGame(self, callback):
		pass
	
	def newGame(self, callback):
		pass
		
	def setAddress(self, address):
		self._address = address
	
	def setCallback(self, callback):
		self._callback = callback
	
	def setPort(self, port):
		self._port = port
	
	def setTimeOut(self, timeout):
		self._timeout = timeout
		
	
				
	#--ClientConnection Private Methods----------------------------------------
	def __readTask(self, taskdata):
		''' This task listens for any messages coming in over any connections.
			If we get a connection passes it to the datagram handler.'''
		if self._cReader.dataAvailable():
			datagram=NetDatagram()  # catch the incoming data in this instance
			# Check the return value; if we were threaded, someone else could have
			# snagged this data before we did
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
		''' This handles incoming messages by calling the appropriate handler.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		if (msgID == MSG_AUTH_RES):
			self.__recieveAuthRes(data, msgID, client)
		#elif (msgID == MSG_CHAT_RES):
		elif (msgID == MSG_GAMELIST_RES):
			self.__recieveGameListRes(data, msgID, client)
		elif (msgID == MSG_NEWGAME_RES):
			self.__recieveNewGameRes(data, msgID, client)
		elif (msgID == MSG_DISCONNECT_REQ):
			self.__recieveDisconnectReq(data, msgID, client)
		else:
			print("Unkown MSG_ID: %d " %msgID),
			print(data)
	
	def __sendAuthReq(self, username, password):
		''' Send user name and password. The password is encypted first using
			SHA256.
			username (String): the username
			password (String): the password (unencrypted)'''
		if self._connected:
			print("Sending authorization")
			h = hashlib.sha256()
			h.update(password)
			pkg = NetDatagram()
			pkg.addUint16(MSG_AUTH_REQ)
			pkg.addString(username)
			pkg.addString(h.hexdigest())
			self._cWriter.send(pkg, self._tcpSocket)
		else:
			print("Cant authorize, we are not connected")
	
	def __recieveAuthRes(self, data, msgID, client):
		''' Recieve the authentication response from the server and deal
			with it by continuing or diconnecting.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		accept = data.getUint32()
		if (accept == 0):
			print("Authorization for server is denied.")
			self.disconnect(None)
		elif (accept == 1):
			print("You are already connected to this server. This could be due to an unclean disconnect.")
		elif (accept == 2):
			print("Authorization granted")
			self._authorized = True
		# Let the requestor know the response then clear the callback
		self._respCallback[MSG_AUTH_RES](accept)
		self._respCallback[MSG_AUTH_RES] = None
	
	def __sendGameListReq(self):
		''' Request a list of games on the connected server.'''
		if (self._connected and self._authorized):
			pkg = NetDatagram()
			pkg.addUint16(MSG_GAMELIST_REQ)
			self._cWriter.send(pkg, self._tcpSocket)
		
	def __recieveGameListRes(self, data, msgID, client):
		''' Recieve the list of games requested.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		games = {}
		indicator = data.getString()
		while (indicator != 'EOT'):
			id          = data.getUint32()
			name        = data.getString()
			maxPlayers  = data.getUint32()
			map         = data.getString()
			startTime   = data.getUint32()
			turnNumber  = data.getUint32()
			indicator   = data.getString()
			games[id] = '%s -  %d - %s - %d - %d'%(name, maxPlayers, map, startTime, turnNumber)
			#print('%d: %s'%(id,games[id]))
		
		# If there is a callback function pass the game list to it
		if self._respCallback[MSG_GAMELIST_RES]:
			self._respCallback[MSG_GAMELIST_RES](games)
		#self._availableGames = games
	
	def __sendNewGameReq(self, name, map, maxplayers):
		''' Create a new game on the server.
			name (String): the name of the game
			map (String): the name of the map
			maxplayers (Int): the max players allowed'''
		print('Sending new game request')
		pkg = NetDatagram()
		pkg.addUint16(MSG_NEWGAME_REQ)
		pkg.addString(name)
		pkg.addString(map)
		pkg.addUint32(maxplayers)
		self._cWriter.send(pkg, self._tcpSocket)
		
	def __recieveNewGameRes(self, data, msgID, client):
		''' Recieve the response of our attempt to create a new game.'''
		print('Recieving new game response')
		game_created = data.getUint32()
		print(game_created)
		if game_created:
			print('Game created successfully')
		elif not game_created:
			print('Game creation failed')
		else:
			print('I do not know what happened to the game')
	
	def __recieveDisconnectReq(self, data, msgID, client):
		print("Server told us it was leaving! Disconecting")
		self._cManager.closeConnection(self.__tcpSocket)
		self._connected = False
		
	def __del__(self):
		''' This destructor tells the server we are leaving so things do not
			get too messy.'''
		self.disconnect()
