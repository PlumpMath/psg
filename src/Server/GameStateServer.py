''' GameStateMgr.py
	
	Author:			Chad Rempp
	Date:			2009/12/31
	License:		GNU LGPL v3
	Todo:			
'''

# Python imports

# PSG imports
from GSEng.Map import *
from GSEng.Game import Game
from Server.ServerConsts import *

class GameStateServer(Game):
	'''A class that keeps track of the game state.'''
	
	def __init__(self, gameName='', numPlayers=0, mapID=''):
		super(GameStateServer, self).__init__()
		
		# Connections relevent to this game
		self.connections = []
		self.mapID = mapID
		
		# Get an ID
		if (len(GAME_IDS) > 0):
			id = GAME_IDS[0]
			GAME_IDS.remove(id)
			self.id = id
		
		if gameName is not '':
			self.name = gameName
		if numPlayers is not '':
			self.numPlayers = numPlayers
		if mapID is not '':
			self.loadMap(id=mapID)
	
	def __del__(self):
		# Release game ID
		if (len(GAME_IDS) < MAX_GAMES):
			GAME_IDS.append(self.id)
			GAME_IDS.sort()
	
	def addPlayer(self, client):
		self.connections.append(client)
	
	def isPlayerInGame(self, client):
		return client in self.connections
		
	def removePlayer(self, client):
		if client in self.connections:
			self.connections.remove(client)
			
	def startGame(self):
		self.startTime = time.time()
		
	def route(self, data, msgID, client):
		self.__handleDatagrame(data, msgID, client)
	
	def __handleDatagram(self, data, msgID, client):
		''' This handles incoming messages.
			
			Run the appropriate handler.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that this datagram came from'''
		if  (msgID == MSG_CHAT_SEND):
			self._console.printNotice('Notice: MSG_CHAT_REQ')
			self.__handleChat(data, msgID, client)
		elif (msgID == MSG_UNITMOVE_SEND):
			self._console.printNotice('Notice: MSG_UNITMOVE_REQ')
			self.__handleUnitMove(data, msgID, client)
		elif (msgID == MSG_UNITATTACK_SEND):
			self._console.printNotice('Notice: MSG_UNITATTACK_REQ')
			self.__handleUnitAttack(data, msgID, client)
		elif (msgID == MSG_UNITINFO_SEND):
			self._console.printNotice('Notice: MSG_UNITINFO_REQ')
			self.__handleUnitInfo(data, msgID, client)
		elif (msgID == MSG_ENDTURN_SEND):
			self._console.printNotice('Notice: MSG_ENDTURN_REQ')
			self.__handleEndTurn(data, msgID, client)
		else:
			self._console.printNotice('%s: Unkown MSG_ID: %d'%(client.getAddress().getIpString(),msgID))
			print(data)
	
	def __handleChat(self, data, msgID, client):
		''' Player chat.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		
	def __handleUnitMove(self, data, msgID, client):
		''' Unit move.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		self._console.printNotice('%s: Unit move request.'%(client.getAddress().getIpString()))
	
	def __handleUnitAttack(self, data, msgID, client):
		''' Unit attack.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		self._console.printNotice('%s: Unit attack request.'%(client.getAddress().getIpString()))
	
	def __handleUnitInfo(self, data, msgID, client):
		''' Unit information.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
		
		self._console.printNotice('%s: Unit information request.'%(client.getAddress().getIpString()))
	
	def __handleEndTurn(self, data, msgID, client):
		''' End turn.
			data (PyDatagramIterator): the list of data sent with this datagram
			msgID (Int): the message ID
			client (Connection): the connection that tendNehis datagram came from'''
			
		self._console.printNotice('%s: End turn request.'%(client.getAddress().getIpString()))
	