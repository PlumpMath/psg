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
import cPickle
import os

def getPlayerFiles():
	''' Return a list of the map filenames stored in the MAP_PATH.'''
	playerlist = []
	for f in os.listdir(PLAYER_PATH):
		if (os.path.splitext(f)[1] == PLAYER_EXT):
			playerlist.append(f)
	return playerlist

def getPlayerFileName(playername):
	''' Search through the files for the player with the given name.'''
	# First try the obvious
	fileName = playername.replace(' ','') + PLAYER_EXT
	fh = open(PLAYER_PATH + fileName)
	player = cPickle.load(fh)
	if (player.name == playername):
		return fileName
	# Otherwise check all the available files
	else:
		for f in getPlayerfiles():
			fh = open(PLAYER_PATH + fileName)
			player = cPickle.load(fh)
			if (player.name == playername):
				return f
			
def getPlayer(file = "", name = ""):
	if (file is not ""):
		fh = open(PLAYER_PATH + file)
		player = cPickle.load(fh)
		return player
	elif (name is not ""):
		file = getPlayerFileName(name)
		fh = open(PLAYER_PATH + file)
		player = cPickle.load(fh)
		return player
	else:
		return None

# Player------------------------------------------------------------------------
class Player:
	name        = None
	id          = 0
	faction     = 'Gorgons'
	type        = 'ComputerAI'
	AI          = None
	file        = ''
	_gamesPlayed = 0
	_gamesWon    = 0
	_gamesLost   = 0
	_entities = []
	def __init__(self,  name="Player", faction='Gorgons', type='ComputerAI',
				 ai=None, gamesplayed=0, gameswon=0, gameslost=0):
		self.name        = name
		self.faction     = faction
		self.type        = type
		self.AI          = ai
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