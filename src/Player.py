''' Player.py
	Author:			Chad Rempp
	Date:			2009/05/25
	Purpose:		
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			
'''

# Python imports
import os

PLAYER_PATH = 'data/players/'
PLAYER_EXT  = '.plr'

def getPlayerFiles():
	''' Return a list of the map filenames stored in the MAP_PATH.'''
	playerlist = []
	for f in os.listdir(PLAYER_PATH):
		if (os.path.splitext(f)[1] == PLAYER_EXT):
			playerlist.append(f)
	return playerlist

# Player------------------------------------------------------------------------
class Player:
	_name        = None
	_faction     = 'Gorgons'
	_type        = 'ComputerAI'
	_AI          = None
	_gamesPlayed = 0
	_gamesWon    = 0
	_gamesLost   = 0
	_entities = []
	def __init__(self,  name="Player", faction='Gorgons', type='ComputerAI',
				 ai=None, gamesplayed=0, gameswon=0, gameslost=0):
		self._name        = name
		self._faction     = faction
		self._type        = type
		self._AI          = ai
		self._gamesPlayed = gamesplayed
		self._gamesWon    = gameswon
		self._gamesLost   = gameslost
		
	def addEntity(self,  e):
		self._entities.append(e)
		e.setOwner(self)
		
	def delEntity(self,  e):
		try:
			self._entities.remove(entity)
		except:
			pass

# SerializablePlayer------------------------------------------------------------
class SerializablePlayer:
	def __init__(self, name, faction='None', type='ComputerAI', ai='Default',
				 gamesplayed=0, gameswon=0, gameslost=0):
		self.name         = name
		self.faction      = faction
		self.type         = type
		self.ai           = ai
		self._gamesPlayed = gamesplayed
		self._gamesWon    = gameswon
		self._gamesLost   = gameslost