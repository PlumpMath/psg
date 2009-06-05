'''_Game.py____________________________________________________________________
	Author:			Chad Rempp
	Date:			2009/05/25
	Purpose:		Holds the game object.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			
____________________________________________________________________________'''

# Python imports
import hashlib
import os
import time

# PSG imports
import Map

MAX_GAMES  = 50
GAME_IDS = range(1,MAX_GAMES)
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

#_CLIENTGAME_CLASS_____________________________________________________________
class ClientGame:
	''' The game class stores all information for active games.'''
	def __init__(self, id=0, name='New Game', maxplayers=2, mapname='', mapfilename='', starttime=0, turnnumber=0):
		''' Creates a new game.
			id (Int): the unique id of this game
			name (String): the name of this game
			maxplayers (Int): maximum players allowed to participate
			map (String): the file name of the map being used'''
		self.id         = id
		self.name       = name
		self.players    = []
		self.maxPlayers = maxplayers
		self.mapName    = mapname
		self.mapFileName= mapfilename
		self.startTime  = starttime
		self.turnNumber = turnnumber
		if self.mapFileName != '' and os.path.exists(Map.MAP_PATH + self.mapFileName):
			self.mapCheck = Map.getMapMD5(self.mapFileName)
		else:
			self.mapCheck = ''
		self.description  = '%s %s %s %s %s'%(self.name,self.maxPlayers,self.mapName,self.startTime,self.turnNumber)

#_SERVERGAME_CLASS_____________________________________________________________
class ServerGame:
	''' The game class stores all information for active games. It also handles
		passing messages between connected clients.'''
	
	def __init__(self, name='New Game', maxplayers=2, mapname='', mapfilename=''):
		''' Creates a new game.
			id (Int): the unique id of this game
			name (String): the name of this game
			maxplayers (Int): maximum players allowed to participate
			map (String): the file name of the map being used'''
		self.id         = getGameID()
		if (self.id < 0):
			print('Error getting a game ID!')
		self.name       = name
		self.players    = []
		self.maxPlayers = maxplayers
		self.mapName    = mapname
		self.mapFileName= mapfilename
		self.startTime  = int(time.time())
		self.turnNumber = 0
		if self.mapFileName != '' and os.path.exists(Map.MAP_PATH + self.mapFileName):
			self.mapCheck = Map.getMapMD5(self.mapFileName)
		else:
			self.mapCheck = ''

	def setMap(self, mapfilename):
		if (mapfilename != None and mapfilename != ''):
			self.mapFile    = mapfilename.replace(' ','')+'.map'
			self.mapCheck   = hashlib.md5(file('data/maps/'+self.mapFile,'rb').read()).hexdigest()
			
	def addPlayer(self, player):
		''' Adds a player to the game.
			player (User): the user to be added to the game'''
		self.players.append(player)
		
	def __del__(self):
		releaseGameID(self.id)