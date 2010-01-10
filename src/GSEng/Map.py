''' Map.py
	
	The map object
	
	Map ids have two formats lXXXX and gXXXX where X is a hex number. The lXXXX
	form is for "local" maps and the gXXXX is for "global" or server recognized
	maps.
	
	Author:			Chad Rempp
	Date:			2009/05/25
	License:		GNU LGPL v3 
	Todo:			Serialize skybox, lights, camera
'''

# Python imports
import cPickle
import hashlib
import os

# PSG imports
#from Entity import *
#from Player import Player
from GameConsts import *
from Util.Serializable import Serializable

class Map(Serializable):
	''' Hold the map data including all players and objects within the map
	
	The Map object is used to serialize most of the static game data. Map
	objects should not persist. Load the data and let it die.
	
	'''

	_VERSION   = '0.1'
	name       = 'Default Map'
	id         = 0
	numPlayers = 0
	mapSize    = (150,150,80)

	def __init__(self, filename=''):
		if filename is not '':
			self.read(filename)
		else:
			self.playerList  = []
			self.entityList  = []
			self._skybox     = None
			self._lights     = None
			self._camera     = None

class MapStore(object):
	''' Holds and manipulates a collection of available maps.
		
		The mapstore loads each map in its map directory, puts key values in a
		dictionary and then closes the map. This is to prevent massive memory
		usage. When a map is needed at a later time it will be reloaded.'''
	
	availableMaps = []
	
	def __init__(self):
		LOG.notice("Creating MapStore")
		self.rescan()
	
	def rescan(self):
		''' Rescan map directory for maps.
			
			Start fresh and load map data.
		'''
		self.availableMaps = []
		
		for f in os.listdir(MAP_PATH):
			if (os.path.splitext(f)[1] == MAP_EXT):
					map = self.loadMap(filename=f)
					dict = {'id':self.getMapMD5(f), 'filename':f, 'name':map.name, 'obj':None}
					self.availableMaps.append(dict)
	
	def getMapDict(self, filename='', id='', name=''):
		''' Return the map dictionary with the filename or id.'''
		for m in self.availableMaps:
			if (filename is not '' and m['filename'] == filename):
				return m
			if (name is not '' and m['name'] == name):
				return m
			if (id != '' and m['id'] == id):
				return m
		return None
	
	def isAvailable(self, filename='', id='', name=''):
		''' Is the map with filename or id available in the availableMaps
		list?'''
		if self.getMapDict(filename=filename, id=id, name=name) is not None:
			return True
		else:
			return False
	
	def isLoaded(self, filename='', id='', name=''):
		''' Is the map with filename or id in the availableMaps list loaded?'''
		map = self.getMapDict(filename=filename, id=id)
		if map is not None and map['obj'] is not None:
			return True
		else:
			return False
		
	def loadMap(self, filename):
		'''Loads the map object and returns it.
		   If the map is not available None is returned.'''
		mDict = self.getMapDict(filename=filename)
		if mDict is not None:
			if mDict['obj'] is not None:
				return mDict['obj']
			else:
				mDict['obj'] = Map("%s%s"%(MAP_PATH,filename))
				return mDict['obj']
		else:
			m = Map("%s%s"%(MAP_PATH,filename))
			return m

	def getMapMD5(self, filename):
		''' Return the MD5 checksum for the given mapfile.'''
		file = open(MAP_PATH + filename, 'rb')
		check = hashlib.md5(file.read()).hexdigest()
		return check
	
	def getAvailableFiles(self):
		''' Return a list of filenames for available maps.
			
			This is needed by the GUI code.'''
		return [map['filename'] for map in self.availableMaps]
		
	def getAvailableNames(self):
		''' Return a list of names for available maps.
		
			This is needed by the GUI code.'''
		return [map['name'] for map in self.availableMaps]
	
	def __str__(self):
		rpr = '<MapStore: %d maps available>\n'
		for map in self.availableMaps:
			rpr += '    <Map: id=%s name=%s file=%s>'%(map['id'],map['name'],map['filename'])
		return rpr