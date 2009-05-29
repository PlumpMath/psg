''' Map.py
	Author:			Chad Rempp
	Date:			2009/05/25
	Purpose:		Holds the map object.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			
	'''

# PSG imports
from Entity import *
from Player import Player
from Representation import *
	
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
	
	def getMap(self):
		''' Create relevant objects for each dictionary entry in each
			dictionary and return lists of the created objects.'''
		
		print("planets %s"%str(self._planets))
		
		playerObjs = []
		planetObjs = []
		planetReps = []
		shipObjs   = []
		shipReps   = []
		
		# Create players
		for playerDict in self._players:
			p = Player(name=playerDict['name'],
					   faction=playerDict['faction'],
					   type=playerDict['type'],
					   ai=playerDict['ai'])
			playerObjs.append(p)
		
		# Create planets
		for planetDict in self._planets:
			e = EntityPlanet(pos=planetDict['pos'],
							 hpr=planetDict['hpr'],
							 owner=planetDict['owner'])
			r = RepPlanet(entity=e,
						  pos=planetDict['pos'],
						  hpr=planetDict['hpr'],
						  model=planetDict['rep'])
			planetObjs.append(e)
			planetReps.append(r)
		
		# Create ships
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
			r = eval('Rep'+shipDict['type'])\
							(entity=e,
							 pos=planetDict['pos'],
							 hpr=planetDict['hpr'],
							 model=planetDict['rep'])
			
		planets = (planetObjs,planetReps)
		ships   = (shipObjs,shipReps)
		return (playerObjs, planets, ships)
		
	def getMapDicts(self):
		''' Just return each list of dictionaries.'''
		return (self._players, self._planets, self._ships)