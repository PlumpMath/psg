''' GameClient.py
	Author:			Chad Rempp
	Date:			2009/05/07
	Purpose:		The game client initializes all the game models and provides
					the interface to a connected game server, either local or
					remote.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			TODO - Make the PSGServer a singleton.
	'''

import direct.directbase.DirectStart
from direct.task import Task
from pandac.PandaModules import QueuedConnectionManager
from pandac.PandaModules import QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader
from pandac.PandaModules import ConnectionWriter
from pandac.PandaModules import NetDatagram
#from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
import hashlib
import time, sys

ADDRESS = "127.0.0.1"
PORT    = 9099 #TCP/IP port to listen on
BACKLOG = 100  #If we ignore this many connection attempts, something is wrong!
TIMEOUT = 3000

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

USER = "chad"
PASS = "password1"

class PSGClient:
	''' The game client. This class sets up most of the game and creates the
		communication links between different modules.'''
	_connected     = False
	_authorized    = False
	_connectedGame = None
	_availableGames = {}
	
	def __init__(self):
		''' Initialize the client.'''
		print("Starting PSG Client ...")
		self._cManager = QueuedConnectionManager()
		self._cListener = QueuedConnectionListener(self._cManager, 0)
		self._cReader = QueuedConnectionReader(self._cManager, 0)
		self._cWriter = ConnectionWriter(self._cManager,0)
		print("Client initialized")
		
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
	
	def connect(self, address, port, timeout):
		''' Try to connect to the server.
			address (String): address for the server
			port (Int): port to connect to
			timeout (Int): how long to wait before giving up (milliseconds)'''
		if self._connected:
			print("Already Connected!")
		try:
			self._tcpSocket = self._cManager.openTCPClientConnection(address, port, timeout)
			self._cReader.addConnection(self._tcpSocket)  # receive messages from server
			taskMgr.add(self.__readTask,"Poll the connection reader",-40)
			self._connected = True
		except:
			print("Couldn't connect to server")
			self._connected = False
	
	def disconnect(self):
		''' Disconnect from the server.'''
		if self._connected:
			print('Disconnecting...')
			pkg = NetDatagram()
			pkg.addUint16(MSG_DISCONNECT_REQ)
			self._cManager.closeConnection(self.__tcpSocket)
			self._connected = False
		else:
			print('Can not disconnect, we are not connected.')
	
	def sendAuthReq(self, username, password):
		''' Send user name and password. The password is encypted first using
			SHA256.
			username (String): the username
			password (String): the password (unencrypted)'''
		if self._connected:
			print("Sending authorization")
			h = hashlib.sha256()
			h.update(PASS)
			pkg = NetDatagram()
			pkg.addUint16(MSG_AUTH_REQ)
			pkg.addString(USER)
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
			self.__disconnect()
		elif (accept == 1):
			print("You are already connected to this server. This could be due to an unclean disconnect.")
		elif (accept == 2):
			print("Authorization granted")
			self._authorized = True
	
	def sendGameListReq(self):
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
			games[id] = '%s -  %d - %s - %d - %d'%(name, maxPlayers, map, startTime, turnNumber)
			print('%d: %s'%(id,games[id]))
		self._availableGames = games
	
	def sendNewGameReq(self, name, map, maxplayers):
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

c = PSGClient()

c.connect(ADDRESS,PORT,TIMEOUT)
c.sendAuthReq(USER,PASS)

taskMgr.doMethodLater(3, c.sendNewGameReq, 'Delayed NEWGAME_REQ', extraArgs=('Test Game','Test Map',3))
run()
