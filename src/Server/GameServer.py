''' GameServer.py
	
	The game server handles sharing games between connected	clients and passes
	messages.
	
	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			* Document the communication protocol (and make it
					  consistent).
					* Make the PSGServer a singleton.
					* Add a clean command to clear abandoned connections
					* Add a periodic ping to check dead connections
					* Add command to turn on/off notices (change log levels)
					* Make the command line work in windows!
					* Break me apart
'''

# Python imports

import os
import sys
import time

# Panda imports
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
from GSEng.Map import Map, MapStore
from Server.ServerPlayer import ServerPlayer
from Server.GameStateServer import GameStateServer
from Server.InterfaceConsole import InterfaceConsole
from Protocol import *
from Server.GameStateServer import GameStateServer
from Server.ServerConsts import *
from Util.Log import LogConsole

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
	# games is a list of active GameStateServer objects
	games = []

	def __init__(self):
		''' Initialize the server.'''
		
		import __builtin__
		__builtin__.LOG = LogConsole()
		
		print('Starting PSG Server ...')
		self._cManager  = QueuedConnectionManager()
		self._cListener = QueuedConnectionListener(self._cManager, 0)
		self._cReader   = QueuedConnectionReader(self._cManager, 0)
		self._cWriter   = ConnectionWriter(self._cManager,0)
		
		#TODO - Load user file (DB)
		self.registeredUsers =[ServerPlayer('chad','password1'),
							   ServerPlayer('josh','password2'),
							   ServerPlayer('james','password3')]
		
		# Map store
		self._mapStore = MapStore()
		
		# Open socket
		self._tcpSocket = self._cManager.openTCPServerRendezvous(PORT,BACKLOG)
		self._cListener.addConnection(self._tcpSocket)
		
		# Setup interfaces
		self._console = InterfaceConsole(self)
		
		# Setup system tasks
		taskMgr.add(self.__listenTask, 'serverListenTask', -40)
		taskMgr.add(self.__readTask, 'serverReadTask', -39)
		taskMgr.doMethodLater(PING_DELAY, self.__pingTask, 'serverPingTask', sort=-41)
		taskMgr.doMethodLater(1, self.__checkPingRespTask, 'serverCheckPingRespTask', sort=-10)
		
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
				if newConnection not in self.connections:
					self.connections.append(newConnection)
					self._cReader.addConnection(newConnection)     # Begin reading connection
					self._console.printNotice('Connection from %s'%netAddress.getIpString())
				else:
					self._console.printNotice('%s: already connected'%(newConnection.getAddress().getIpString()))
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
		
		notice = 'Pinging: '
		
		for c in self.connections:
			# Don't ping connections we're still waiting on
			if c not in self.pingNonResponders.keys():
				notice = '%s%s '%(notice, c.getAddress().getIpString())
				self.pingNonResponders[c] = int(time.time())
				pkg = NetDatagram()
				pkg.addUint16(MSG_PING_REQ)
				self._cWriter.send(pkg, c)
		
		LOG.notice(notice)
		# Add task back into the taskmanager
		taskMgr.doMethodLater(PING_DELAY, self.__pingTask, 'serverPingTask', sort=-41)
		
	def __checkPingRespTask(self, Task):
		''' Run through the list of connections that haven't responded to their
			ping yet and disconnect them if has been more than PING_TIMEOUT
			seconds.'''
		
		notice = 'Cleaning non-responders '
		
		for c in self.pingNonResponders.keys():
			notice = '%s%s '%(notice, c.getAddress().getIpString())
			now = int(time.time())
			pingTime = self.pingNonResponders[c]
			if ((now - pingTime) > PING_TIMEOUT):
				#print('disconnecting '),
				self.__handleDisconnect(None, None, c)
		
		LOG.notice(notice)
		# Add task back into the taskmanager
		taskMgr.doMethodLater(1, self.__checkPingRespTask, 'serverCheckPingRespTask', sort=-10)
	
	def __handleDatagram(self, data, msgID, client):
		''' This handles incoming messages. It can run the appropriate handler
			from the server or pass it to the relevant game to deal with.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		self._console.printNotice('%s: Recieved msg: %d'%(client.getAddress().getIpString(),msgID))
		# System messages
		if (msgID == MSG_PING_REQ):
			self._console.printNotice('Notice: MSG_PING_REQ')
			self.__handlePingReq(data, msgID, client)
		elif (msgID == MSG_PING_RES):
			self._console.printNotice('Notice: MSG_PING_RES')
			self.__handlePingRes(data, msgID, client)
		elif (msgID == MSG_DISCONNECT_REQ):
			self._console.printNotice('Notice: MSG_DISCONNECT_REQ')
			self.__handleDisconnect(data, msgID, client)
		# Pre-game server messages
		elif (msgID == MSG_AUTH_REQ):
			self._console.printNotice('Notice: MSG_AUTH_REQ')
			self.__handleAuth(data, msgID, client)
		elif (msgID == MSG_MAPLIST_REQ):
			self._console.printNotice('Notice: MSG_MAPLIST_REQ')
			#self.__handleMapList(data, msgID, client)
		elif (msgID == MSG_GAMELIST_REQ):
			self._console.printNotice('Notice: MSG_GAMELIST_REQ')
			self.__handleGameList(data, msgID, client)
		elif (msgID == MSG_NEWGAME_REQ):
			self._console.printNotice('Notice: MSG_NEWGAME_REQ')
			self.__handleNewGame(data, msgID, client)
		elif (msgID == MSG_JOINGAME_REQ):
			self._console.printNotice('Notice: MSG_JOINGAME_REQ')
			self.__handleJoinGame(data, msgID, client)
		elif (msgID >= MSG_INGAME):
			self.__route(data, msgID, client)
		else:
			self._console.printNotice('%s: Unkown MSG_ID: %d'%(client.getAddress().getIpString(),msgID))
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
		
		self._console.printNotice('%s: Ping request'%(client.getAddress().getIpString()))
		
	def __handlePingRes(self, data, msgID, client):
		''' Handle an incoming ping response.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
			
		# Client responded so remove from non-responder list
		del(self.pingNonResponders[client])
		self._console.printNotice('%s: Ping response'%(client.getAddress().getIpString()))
	
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
			
		# Don't worry about pings any more
		if client in self.pingNonResponders:
			del(self.pingNonResponders[client])
		
		self._console.printNotice('%s: Disconnected user %s'%(client.getAddress().getIpString(),username))
	
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
					self._console.printNotice('%s: User %s already connected'%(client.getAddress().getIpString(),username))
					break
				elif u.password != password:
					auth = 2
					self._console.printNotice('%s: User %s gave invalid password'%(client.getAddress().getIpString(),username))
					break
				else:
					auth = 3
					u.connect(client)
					self.connectedUsers.append(u)
					self._console.printNotice('%s: User %s connected with pass %s' %(client.getAddress().getIpString(),username,password))
		
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
		
		self._console.printNotice('%s: Request for map list.' %(client.getAddress().getIpString()))
	
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
				pkg.addInt32(g.id)
				pkg.addString(g.name)
				pkg.addUint32(g.numPlayers)
				pkg.addString(g.map.name)
				pkg.addString(g.mapFile)
				pkg.addUint32(g.startTime)
				pkg.addUint32(g.turnNumber)
				if i < len(self.games)-1:
					pkg.addString('T') # Still tranmitting
			pkg.addString('EOT') # End Of Transmission
		self._cWriter.send(pkg, client)
		
		self._console.printNotice('%s: Request for game list.' %(client.getAddress().getIpString()))
		
	def __handleNewGame(self, data, msgID, client):
		''' Create a new game and respond with success or failure.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		# Unpack message data
		gameName    = data.getString()
		mapID       = data.getString()
		numPlayers  = data.getUint32()
		
		# If we do not have the map for the requested game tell client
		if(not self._mapStore.isAvailable(id=mapID)):
			response = 0
		else:
			# Create the game
			newGame = GameStateServer(gameName, numPlayers, mapID)
			if newGame is not None:
				self.games.append(newGame)
				response = newGame.id
			else:
				response = -1
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_NEWGAME_RES)
		pkg.addInt32(response)
		self._cWriter.send(pkg, client)
		
		self._console.printNotice('%s: Request for new game: %s, %s, %d.' %(client.getAddress().getIpString(),gameName,mapID,numPlayers))
		
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
			LOG.debug('No such game')
			resp = 0
		elif len(game.players) >= game.maxPlayers:
			LOG.debug('Game full')
			resp = 1
		else:
			game.addPlayer(client)
			LOG.debug('Ok, joining game')
			resp = 2
		
		# Send response
		pkg = NetDatagram()
		pkg.addUint16(MSG_JOINGAME_RES)
		pkg.addUint32(resp)
		self._cWriter.send(pkg, client)
		self._console.printNotice('%s: Request to join game id %d, gave %d.'%(client.getAddress().getIpString(),id,resp))
		
	def __route(self, data, msgID, client):
		LOG.notice('Routing msg to GameStateServer')
		
	def shutdown(self):
		print('Shutting down server ...')
		
		# Send disconnect to all clients
		pkg = NetDatagram()
		pkg.addUint16(MSG_DISCONNECT_REQ)
		for c in self.connections:
			self._cWriter.send(pkg, c)
		self._cManager.closeConnection(self._tcpSocket)
		print('Server done')
		sys.exit()
		
	def disconnect(self, client):
		''' Disconnect client'''
		self.__handleDisconnect(None, None, client)
