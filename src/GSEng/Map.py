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

def getMapFiles():
	''' Return a list of the map filenames stored in the MAP_PATH.'''
	maplist = []
	for f in os.listdir(MAP_PATH):
		if (os.path.splitext(f)[1] == MAP_EXT):
			maplist.append(f)
	return maplist

def getMapMD5(mapfilename):
	''' Return the MD5 checksum for the given mapfile.'''
	file = open(MAP_PATH + mapfilename, 'rb')
	check = hashlib.md5(file.read()).hexdigest()
	return check

def getMapFileName(mapname):
	''' Search through the files for the game with the given name.'''
	
	# First try the obvious
	fileName = mapname.replace(' ','') + MAP_EXT
	fh = open(MAP_PATH + fileName)
	map = cPickle.load(fh)
	if (map.name == mapname):
		return fileName
	# Otherwise check all the available files
	else:
		for f in getMapfiles():
			fh = open(MAP_PATH + fileName)
			map = cPickle.load(fh)
			if (map.name == mapname):
				return f

class Map(Serializable):
	''' Hold the map data including all players and objects within the map
	
	The Map object is used to serialize most of the static game data. Map
	objects should not persist. Load the data and let it die.
	
	cPickle will not follow object references so to serialize the players and
	entities it is necessary to include the serialized data for each directly
	in this object.
	'''

	_VERSION    = '0.0'
	name        = 'Default Map'
	id          = 0
	playerCount = 0
	mapSize     = (150,150,80)

	def __init__(self):
		self.playerList  = []
		self.entityList  = []
		self._skybox     = None
		self._lights     = None
		self._camera     = None


class MapStore(object):
	''' Collection of available maps
	
	'''
	availableMaps = list()
	
	def __init__(self):
		pass
	
	def rescan(self):
		''' Rescan map directory for maps. If a map with the filename already
		exists in availableMaps nothing is done. Otherwise the filename is
		stored. Not that the map is not loaded at this point.
		'''
		for f in os.listdir(MAP_PATH):
			if (os.path.splitext(f)[1] == MAP_EXT):
				if not(self.isAvailable(f)):
					availableMaps.append({'filename':f, 'id':'', 'obj':None, 'md5':self.getMapMD5(f)})
	
	def isAvailable(self, filename='', id=''):
		''' Is the map with filename or id available in the availableMaps
		list?'''
		if self.getMapDict(filename=filename, id=id) != None:
			return True
		else:
			return False
	
	def isLoaded(self, filename='', id=''):
		''' Is the map with filename or id in the availableMaps list loaded?'''
		if self.getMapDict(filename=filename, id=id)['obj'] != None:
			return True
		else:
			return False
		
	def getMapDict(self, filename='', id=''):
		''' Return the map dictionary with the filename or id.'''
		for m in self._availableMaps:
			if (filename is not '' and m['filename'] == filename):
				return m
			if (id != '' and m['id'] == id):
				return m
		return None
			
	def getMap(self, filename='', id=''):
		''' Return the map instance with the filename or id. If the map is not
		loaded None is returned.'''
		return self.getMapDict(filename=filename, id=id)['obj']
		
	def loadMap(self, filename='', id=''):
		''' If the map with filename or id is available it is loaded and the
		map object is returned. If the map is not available None is returned.'''
		mapDict = self.getMapDict(filename, id)
		if mapDict is not None:
			if filename is not '' and mapDict[filename] is not filename:
				mapDict['filename'] = filename
			m = Map()
			m.read(mapDict['filename'])
			mapDict['obj'] = m
			return m
		else:
			return None

	def getMapMD5(filename):
		''' Return the MD5 checksum for the given mapfile.'''
		file = open(MAP_PATH + filename, 'rb')
		check = hashlib.md5(file.read()).hexdigest()
		return check