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


class Map(object):
	''' Hold the map data including all players and objects within the map
	
	The Map object is used to serialize most of the static game data.
	'''

	#VERSION    = '0.1'
	#name       = 'New Map'
	#numPlayers = 0
	#mapSize    = (150,150,80)
	#playerList = []
	#entityList = []
	#skybox     = None
	#lightList  = []
	#cameraList = []
	
	def __init__(self, filename=''):
		self.VERSION    = '0.1'
		self.name       = ''
		self.numPlayers = 0
		self.mapSize    = (150,150,80)
		
		# playerList is a list of Player objects
		self.playerList = []
		
		# entityList is a list of Entity objects
		self.entityList = []
		
		# skybox is a SkyBox object
		self.skybox     = None
		
		# lightList is a list of dictionarties defining lights. These are not
		# instances so they must be instantiated
		self.lightList  = []
		
		# cameraList is a list of camera objects
		self.cameraList = []
		
		#if filename is not '':
		#	self.read(filename)
		print("name=%s"%self.name)

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
			#print("Checking %s"%f)
			if (not f.startswith('.') and os.path.splitext(f)[1] == MAP_EXT):
				#print("  adding %s"%f)
				map = self.loadMap(filename=f)
				dict = {'id':self.getMapMD5(f), 'filename':f, 'name':map.name, 'numplayers':map.numPlayers}
				self.availableMaps.append(dict)
		#print(self.availableMaps)
	
	def getMap(self, id='', filename='', name=''):
		''' Return the map dictionary matching on given parameters.'''
		for mapDict in self.availableMaps:
			if (id is not '' and mapDict['id'] == id):
				return mapDict
			if (filename is not '' and mapDict['filename'] == filename):
				return mapDict
			if (name is not '' and mapDict['name'] == name):
				return mapDict
		return None
		
	def getId(self, filename='', name=''):
		''' Return the map id for the map matching the given parameters.'''
		for m in self.availableMaps:
			if (filename is not '' and m['filename'] == filename):
				return m
			if (name is not '' and m['name'] == name):
				return m
		return None
	
	def isAvailable(self, id='', filename='', name=''):
		''' Is the map with given parameters in the availableMaps list?'''
		
		for m in self.availableMaps:
			if (id is not '' and m['id'] == id):
				return True
			if (filename is not '' and m['filename'] == filename):
				return True
			if (name is not '' and m['name'] == name):
				return True
		return False
	
	def loadMap(self, filename):
		'''Loads the map object, unpickles and returns it.
		   If the map is not available None is returned.'''
		
		fullPath = "%s%s"%(MAP_PATH,filename)
		m = None
		
		if (os.path.exists(fullPath)):
			try:
				fh = open(fullPath, 'rb')
				try:
					m = cPickle.load(fh)
				except cPickle.UnpicklingError as (errno, strerror):
					LOG.error("Could not read file: %s [%s]"%(fullPath,strerror))	
			except IOError as (errno, strerror):
				LOG.error("Could not open file: %s [%s]"%(fullPath,strerror))
			else:
				fh.close()
		else:
			LOG.error("Map file does not exist: %s"%(file))
		
		return m
	
	def loadMapAsString(self, filename):
		'''Loads the map object as a string and returns it.
		   If the map is not available None is returned. This is meant for
		   sending maps to clients.'''
		
		fullPath = "%s%s"%(MAP_PATH,filename)
		m = None
		
		if (os.path.exists(fullPath)):
			try:
				fh = open("%s%s"%(MAP_PATH,filename), 'rb')
				m = fh.read()
			except IOError as (errno, strerror):
				LOG.error("Could not open file: %s [%s]"%(fullPath,strerror))
			else:
				fh.close()
				
		return m
	
	def writeMap(self, filename, map):
		''' Pickle map and write to file. We must attach the file handle
			to the class so we can easily remove it before pickling.'''
		
		fullPath = "%s%s"%(MAP_PATH,filename)
		
		try:
			fh = open(fullPath, 'wb')
			try:
				cPickle.dump(self,fh,2)
			except cPickle.PicklingError as (errno, strerror):
				LOG.error("Could not write file: %s [%s]"%(fullPath,strerror))
		except IOError as (errno, strerror):
			LOG.error("Could not open file: %s [%s]"%(fullPath,strerror))
		else:
			fh.close()
			
	def getMapMD5(self, filename):
		''' Return the MD5 checksum for the given mapfile.'''
		file = open(MAP_PATH + filename, 'rb')
		check = hashlib.md5(file.read()).hexdigest()
		return check
	
	def getAvailableFiles(self):
		''' Return a list of filenames for available maps (needed by GUI).'''
		return [map['filename'] for map in self.availableMaps]
		
	def getAvailableNames(self):
		''' Return a list of names for available maps (needed by GUI).'''
		return [map['name'] for map in self.availableMaps]
	
	def __str__(self):
		rpr = '<MapStore: %d maps available>\n'
		for map in self.availableMaps:
			rpr += '    <Map: id=%s name=%s file=%s>'%(map['id'],map['name'],map['filename'])
		return rpr