''' Game.py
	
	Base game class.
	
	Author:			Chad Rempp
	Date:			2010/01/01
	License:		GNU LGPL v3
	Todo:			
'''

# Python imports
#import hashlib
import os
import time

# PSG imports
from game.GSEng.Map import MapStore, Map
from game.GameConsts import *

class Game(object):
	''' The game class stores the basic information for games.'''
	def __init__(self):
		''' Creates a new game.'''
		self.id          = -1
		self.name        = ''
		self.numPlayers  = 0
		self.turnNumber  = 0
		self.startTime   = 0
		self.mapFile     = ''
		self.map         = None
		self.mapSize     = None
		
		self._mapStore = MapStore()
		
	def loadMap(self, filename='', id=''):
		''' Load the map
			
			TODO - Can this be removed?
		'''
		if id is not '':
			self.mapFile = self._mapStore.getMap(id=id)['filename']
			self.map = self._mapStore.loadMap(self.mapFile)
		if filename is not '':
			self.mapFile = filename
		if self.mapFile is not '' and os.path.exists(MAP_PATH + self.mapFile):
			self.map = self._mapStore.loadMap(self.mapFile)
		
	def runTime(self):
		if self.startTime > 0:
			return time.time() - self.startTime
		else:
			return self.startTime
		
	def __repr__(self):
		r = "<ClientGame: id=%d, name=%s, numPlayers=%d, "%(self.id, self.name, self.numPlayers)
		r+= "startTime=%s, turnNumber=%d "%(self.startTime, self.turnNumber)
		r+= "mapFile=%s>"%self.mapFile
		return r