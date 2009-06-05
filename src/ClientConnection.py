''' ClientConnection.py
	Author:			Chad Rempp
	Date:			2009/05/09
	Purpose:		The ClientConnection connects to a game server and passes
                	messages between the game and the server.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			TODO - Add timer to callbacks for timeouts
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

# PSG imports
from Game import *
from Protocol import *

PING_DELAY = 60 # Seconds between pinging connections
PING_TIMEOUT = 10 # Seconds to wait for a ping response

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
	_respCallback   = {MSG_AUTH_RES:       None,
					   MSG_MAPLIST_RES:    None,
					   MSG_GAMELIST_RES:   None,
					   MSG_NEWGAME_RES:    None,
					   MSG_JOINGAME_RES:   None}
	def __init__(self):
		self._cManager   = QueuedConnectionManager()
		self._cListener  = QueuedConnectionListener(self._cManager, 0)
		self._cReader    = QueuedConnectionReader(self._cManager, 0)
		self._cWriter    = ConnectionWriter(self._cManager,0)
		
	#--Object Interface--------------------------------------------------------
	def getAddress(self):
		return self._address
	
	def getPort(self):
		return self._port
		
	def getTimeout(self):
		return self._timeout
	
	def isConnected(self):
		return self._connected
	
	def setAddress(self, address):
		self._address = address
	
	def setPort(self, port):
		self._port = port
	
	def setTimeOut(self, timeout):
		self._timeout = timeout
	
	#--Communication Interface-------------------------------------------------
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
			taskMgr.doMethodLater(PING_DELAY, self.__pingTask, 'serverPingTask', sort=-41)
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
	
	def getMapList(self, callback):
		''' Send a request for a list of maps available on the server.
			The server will return a list in the form
			(filename,mapname,md5sum)'''
		self.__sendMapListReq()
		self._respCallback[MSG_MAPLIST_RES] = callback
	
	def getGameList(self, callback):
		''' Sends a request for a list of active games to the server.
			On success callback is passed a dictionary of the form,
			{id: 'descriptive string'}.'''
		self.__sendGameListReq()
		self._respCallback[MSG_GAMELIST_RES] = callback
		
	def newGame(self, gamename, mapname, mapfilename, maxplayers, callback):
		''' Send info to start a new game on the server.'''
		self.__sendNewGameReq(gamename, mapname, mapfilename, maxplayers)
		self._respCallback[MSG_NEWGAME_RES] = callback
		
	def joinGame(self, gameid, callback):
		''' Attempt to join the game with ID=gameid.'''
		self.__sendJoinGameReq(gameid)
		self._respCallback[MSG_JOINGAME_RES] = callback
	
	def sendUnitMove(self, movedentity, callback):
		''' Send updated entity to server.'''
		self.__sendUnitMove(movedentity)
		self._respCallback[MSG_UNITMOVE_RES] = callback
		
	def sendUnitAttack(self, fromentity, toentity, callback):
		''' Send a message that fromentity attacked toentity. The entities
			have been updated from the attack.'''
		self.__sendUnitAttack(fromentity, toentity)
		self._respCallback[MSG_UNITATTACK_RES] = callback
		
	def sendUnitInfo(self, entity):
		''' Send a requst for information about the given entity.'''
		self.__sendUnitInfo(entity)
		self._respCallback[MSG_UNITINFO_RES] = callback
		
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
	
	def __pingTask(self, Task):
		''' Ping the server every PING_DELAY seconds to check if it's still
			there.'''
		print('Pinging')
		
		# Add task back into the taskmanager
		taskMgr.doMethodLater(PING_DELAY, self.__pingTask, 'serverPingTask', sort=-41)

	def __handleDatagram(self, data, msgID, client):
		''' This handles incoming messages by calling the appropriate handler.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		if (msgID == MSG_PING_REQ):
			self.__recievePingReq(data, msgID, client)
		elif (msgID == MSG_DISCONNECT_REQ):
			self.__recieveDisconnectReq(data, msgID, client)
		elif (msgID == MSG_AUTH_RES):
			self.__recieveAuthRes(data, msgID, client)
		elif (msgID == MSG_MAPLIST_RES):
			self.__recieveMapListRes(data, msgID, client)
		elif (msgID == MSG_GAMELIST_RES):
			self.__recieveGameListRes(data, msgID, client)
		elif (msgID == MSG_NEWGAME_RES):
			self.__recieveNewGameRes(data, msgID, client)
		elif (msgID == MSG_JOINGAME_RES):
			self.__recieveJoinGameRes(data, msgID, client)
		elif (msgID == MSG_CHAT_RECV):
			self.__recieveChatRes(data, msgID, client)
		elif (msgID == MSG_UNITMOVE_RECV):
			self.__recieveUnitMove(data, msgID, client)
		elif (msgID == MSG_UNITATTACK_RECV):
			self.__recieveUnitAttack(data, msgID, client)
		elif (msgID == MSG_UNITINFO_RECV):
			self.__recieveUnitInfo(data, msgID, client)
		elif (msgID == MSG_ENDTURN_RECV):
			self.__recieveEndTurn(data, msgID, client)
		else:
			print("Unkown MSG_ID: %d " %msgID),
			print(data)
	
	def __recievePingReq(self, data, msgID, client):
		''' Handle pings from the server.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		
		print("Recieved a ping request")
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_PING_RES)
		self._cWriter.send(pkg, self._tcpSocket)
	
	def __recieveDisconnectReq(self, data, msgID, client):
		''' Handle a disconnect request from the server.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
			
		print("Server told us it was leaving! Disconecting")
		
		self._cManager.closeConnection(self._tcpSocket)
		self._connected = False
	
	def __sendAuthReq(self, username, password):
		''' Send user name and password. The password is encypted first using
			SHA256.
			username (String): the username
			password (String): the password'''
			
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
		
		# Unpack message data
		accept = data.getUint32()
		
		if (accept == 0):
			print("Authorization for server failed for an unknown reason.")
			self.disconnect(None)
		elif (accept == 1):
			print("You are already connected to this server. This could be due to an unclean disconnect.")
		elif (accept == 2):
			print("Incorrect password")
		elif (accept == 3):
			print("Authorization granted.")
			self._authorized = True
		
		# If there is a callback function pass the game list to it
		if self._respCallback[MSG_AUTH_RES]:
			self._respCallback[MSG_AUTH_RES](accept)
			self._respCallback[MSG_AUTH_RES] = None
	
	def __sendGameListReq(self):
		''' Request a list of games on the connected server.'''
		
		# Send request
		if (self._connected and self._authorized):
			pkg = NetDatagram()
			pkg.addUint16(MSG_GAMELIST_REQ)
			self._cWriter.send(pkg, self._tcpSocket)
		
	def __recieveGameListRes(self, data, msgID, client):
		''' Recieve the list of games requested.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		
		games = []
		
		# Unpack message data
		indicator = data.getString()

		while (indicator != 'EOT'):
			id          = data.getUint32()
			name        = data.getString()
			maxPlayers  = data.getUint32()
			mapName     = data.getString()
			mapFileName = data.getString()
			startTime   = data.getUint32()
			turnNumber  = data.getUint32()
			indicator   = data.getString()
			games.append(ClientGame(id=id,
									name=name,
									maxplayers=maxPlayers,
									mapname=mapName,
									mapfilename=mapFileName,
									starttime=startTime,
									turnnumber=turnNumber))
			
		# If there is a callback function pass the game list to it
		if self._respCallback[MSG_GAMELIST_RES]:
			self._respCallback[MSG_GAMELIST_RES](games)
		#self._availableGames = games
	
	def __sendNewGameReq(self, gamename, mapname, mapfilename, maxplayers):
		''' Create a new game on the server.
			name (String): the name of the game
			map (String): the name of the map
			maxplayers (Int): the max players allowed'''
			
		print('Sending new game request %s'%map)
		
		# Send Request
		if (self._connected and self._authorized):
			pkg = NetDatagram()
			pkg.addUint16(MSG_NEWGAME_REQ)
			pkg.addString(gamename)
			pkg.addString(mapname)
			pkg.addString(mapfilename)
			pkg.addUint32(maxplayers)
			self._cWriter.send(pkg, self._tcpSocket)
		
	def __recieveNewGameRes(self, data, msgID, client):
		''' Recieve the response of our attempt to create a new game.'''
		
		print('Recieving new game response')
		
		# Unpack message data
		game_created = data.getUint32()
		
		# If there is a callback function pass the response to it
		if self._respCallback[MSG_NEWGAME_RES]:
			self._respCallback[MSG_NEWGAME_RES](game_created)
			self._respCallback[MSG_NEWGAME_RES] = None
			
	def __sendJoinGameReq(self, id):
		''' Join a game on the server.
			id (int): the id of the game to join'''
			
		print('Sending join game request')
		
		# Send Request
		if (self._connected and self._authorized):
			pkg = NetDatagram()
			pkg.addUint16(MSG_JOINGAME_REQ)
			pkg.addUint32(id)
			self._cWriter.send(pkg, self._tcpSocket)
	
	def __recieveJoinGameRes(self, data, msgID, client):
		''' Handle the response to a join game request.'''
		
		print("Recieving joing game response")
		
		# Unpack message data
		join_response = data.getUint32()
		
		# If there is a callback function pass the response to it
		if self._respCallback[msgID]:
			self._respCallback[msgID](join_response)
			self._respCallback[msgID] = None
	
	def __sendChat(self, message):
		''' Send chat message to the server.'''
		
		print('Sending chat')
		
	def __recieveChat(self, data, msgID, client):
		''' Recieve chat message from server.'''
		
		print('Recieved chat')
	
	def __sendUnitMove(self, entity):
		''' Send the updated entity to the server.'''
		
		print('Sending move')
	
	def __recieveUnitMove(self, data, msgID, client):
		''' Recieve an updated entity.'''
		
		print('Recieved move')
	
	def __sendUnitAttack(self, fromentity, toentity):
		''' Send a an attacking entity (fromentity) and an attacked
			entity (toentity).'''
			
		print('Sending attack')
	
	def __recieveUnitAttack(self, data, msgID, client):
		''' Recieve an attack from the server.'''
		
		print('Recieved attack')
		
	def __sendUnitInfo(self, entity):
		''' Send a request for info on an entity.'''
		
		print('Sending info request')
		
	def __recieveUnitInfo(self, data, msgID, client):
		''' Recieve unit info.'''
		
		print('Recieving unit info')
		
	def __sendEndTurn(self):
		''' Send end turn request.'''
		
		print('Sending end turn')
	
	def __recieveEndTurn(self, data, msgID, client):
		''' Recieve end turn.'''
		
		print('Recieving end turn.')
		
	def __del__(self):
		''' This destructor tells the server we are leaving so things do not
			get too messy.'''
		self.disconnect()
