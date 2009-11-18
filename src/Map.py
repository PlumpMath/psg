'''_Map.py_____________________________________________________________________
	Author:			Chad Rempp
	Date:			2009/05/25
	Purpose:		Provides map file access and returns objects from the map
					files.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		GPL
	Notes:			
____________________________________________________________________________'''

# Python imports
import cPickle
import hashlib
import os

# PSG imports
from Entity import *
from Player import Player

MAP_PATH = 'data/maps/'
MAP_EXT  = '.map'

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

class Map:
	name = 'Default Map'
	file = ''
	mapSize = (150,150,80)
	startingPlanets = 1
	players = []
	planets = []
	ships = []
	
	
class SerializableMap:
	''' The map object is used only for serialization of maps. You can load
		and save maps with this class then use getMap to return the map
		objects.'''
	
	name = 'Default Map'
	mapSize = (150,150,80)
	startingPlanets = 1
	
	_file = ''
	
	# This is a list of dictionarys. Each dictionary has the following keys
	# 'name':    'player name'
	# 'faction': 'faction name'
	# 'type':    'computer or human'
	# 'ai':      'ai name'
	_players = []
	
	# This is a list of dictionarys. Each dictionary has the following keys
	# 'owner': 'player name'
	# 'pos':   'location'
	# 'hpr':   'orientation'
	# 'rep':   'model name'
	_planets = []
	
	# This is a list of dictionarys. Each dictionary has the following keys
	# 'type':  'type', ex. LightCapture, HeavyCapture, this is the end of the class name
	# 'owner': 'player name'
	# 'pos':   'location'
	# 'hpr':   'orientation'
	# 'rep':   'model name'
	# The following modify default starting states for ships
	# 'moveRad':   0
	# 'attackRad': 0
	# 'sensorRad': 0
	# 'fuel':      0
	# 'moved':     False
	# 'attacked':  False
	_ships = []
	
	def addPlayer(self, name, faction='None', type='ComputerAI', ai='Default'):
		''' Add a player dictionary entry to the map. See above for details
			on the dictionary structure.'''
			
		d = {'name':name,
			 'faction':faction,
			 'type':type,
			 'ai':ai}
		self._players.append(d)
	
	def addPlanet(self, pos, hpr=(0,0,0), owner='None', rep='Default'):
		''' Add a planet dictionary entry to the map. See above for details
			on the dictionary structure.'''
			
		d = {'owner':owner,
			 'pos':pos,
			 'hpr':hpr,
			 'rep':rep}
		self._planets.append(d)
	
	def addShip(self, type, pos, hpr=(0,0,0), owner='None', rep='Default',
				moverad=0, attackrad=0, sensorrad=0, fuel=0, moved=False,
				attacked=False):
		''' Add a ship dictionary entry to the map. See above for details
			on the dictionary structure.'''
			
		d = {'type': type,
			 'owner':owner,
			 'pos':pos,
			 'hpr':hpr,
			 'rep':rep,
			 'moveRad':moverad,
			 'attackRad':attackrad,
			 'sensorRad':sensorrad,
			 'fuel':fuel,
			 'moved':moved,
			 'attacked':attacked}
		self._ships.append(d)
	
	def getPlayers(self):
		''' Return a list of Player objects.'''
		
		playerObjs = []
		
		for playerDict in self._players:
			p = Player(name=playerDict['name'],
					   faction=playerDict['faction'],
					   type=playerDict['type'],
					   ai=playerDict['ai'])
			playerObjs.append(p)
			
		return playerObjs
	
	def getPlayerDict(self):
		''' Just return each list the player dictionaries.'''
		return self._players
	
	def getPlanets(self):
		''' Return a list of EntityPlanet objects.'''
		
		planetObjs = []
		
		# Create planets
		for planetDict in self._planets:
			e = EntityPlanet(pos=planetDict['pos'],
							 hpr=planetDict['hpr'],
							 owner=planetDict['owner'])
			planetObjs.append(e)
		
		return planetObjs
	
	def getPlanetDict(self):
		''' Just return each list the planet dictionaries.'''
		return self._planets
	
	def getShips(self):
		''' Return a list of EntityShip objects.'''
		print("SM has %d ships"%len(self._ships))
		shipObjs   = []
		
		for shipDict in self._ships:
			e = eval('Entity'+shipDict['type'])\
							(pos=planetDict['pos'],
							 hpr=planetDict['hpr'],
							 owner=planetDict['owner'])
			if planetDict['moveRad'] != 0: e.moveRad=planetDict['moveRad']
			if planetDict['attackRad'] != 0: e.attackRad=planetDict['attackRad']
			if planetDict['sensorRad'] != 0: e.sensorRad=planetDict['sensorRad']
			if planetDict['sensorRad'] != 0: e.fuel=planetDict['fuel']
			e.moved=planetDict['moved']
			e.attacked=planetDict['attacked']
			
		return shipObjs
		
	def getShipDict(self):
		''' Just return each list the ship dictionaries.'''
		return self._ships

def saveMapSerialized(map, fileName):
	pass

def openMapSerialized(fileName):
	pass

def saveMapText(map, fileName):
	print("Saving Map")
	fh = open(MAP_PATH+fileName, 'wb')
	fh.write("<BEGIN MAP>")
	fh.write("name=%s"%serialMap.name)
	fh.write("mapsizex=%d"%mapSize[0])
	fh.write("mapsizey=%d"%mapSize[1])
	fh.write("mapsizez=%d"%mapSize[2])
	fh.write("startingplanets=%d"%startingPlanets)
	for player in map.getPlayers:
		fh.write("<BEGIN PLAYER>")
		fh.write("player.name=%s"%player.name)
		fh.write("player.file=%s"%player.name)
		fh.write("<END PLAYER>")
	for planet in map.getPlanets:
		fh.write("<BEGIN PLANET>")
		fh.write("planet.owner=%s"%planet.owner)
		fh.write("planet.posx=%d"%planet.pos[0])
		fh.write("planet.posy=%d"%planet.pos[1])
		fh.write("planet.posz=%d"%planet.pos[2])
		fh.write("planet.hprx=%d"%planet.pos[0])
		fh.write("planet.hpry=%d"%planet.pos[1])
		fh.write("planet.hprz=%d"%planet.pos[2])
		fh.write("planet.model=%s"%planet.representation.model)
		fh.write("<END PLANET>")
	for ship in map.getShips:
		fh.write("<BEGIN SHIP>")
		fh.write("ship.owner=%s"%ship.owner)
		fh.write("ship.posx=%d"%ship.pos[0])
		fh.write("ship.posy=%d"%ship.pos[1])
		fh.write("ship.posz=%d"%ship.pos[2])
		fh.write("ship.hprx=%d"%ship.pos[0])
		fh.write("ship.hpry=%d"%ship.pos[1])
		fh.write("ship.hprz=%d"%ship.pos[2])
		fh.write("ship.model=%s"%ship.representation.model)
		fh.write("<END SHIP>")
	fh.write("<END MAP>")
	fh.close()
	
def openMapText(fileName):
	pass