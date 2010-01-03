''' Player.py
	
	
	
	Author:			Chad Rempp
	Date:			2009/05/25
	License:		GNU LGPL v3
	Todo:			
'''

# Python imports
import cPickle
import os

# PSG imports
from Util.Serializable import Serializable

class Player(Serializable):
	id          = 0
	name        = 'New Player'
	faction     = 'Gorgons'
	type        = 'Human'
	AI          = None
	
	isConnected = False
	_gamesPlayed = 0
	_gamesWon    = 0
	_gamesLost   = 0
	
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