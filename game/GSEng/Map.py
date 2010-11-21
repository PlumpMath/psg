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
import sys
import xml.sax

from game.GameConsts import *
from game.GSEng.Player import Player
from game.GSEng import Entity
from game.GameConsts import *
from game.GXEng.CameraMgr import CameraManager
from game.GXEng.SkyBox import SkyBox

# PSG imports
from game.GameConsts import *

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
		
		# Create a map loader
		if (MAP_TYPE.lower() == 'xml'):
			self.mapFacade = MapXMLFacade()
		elif (MAP_TYPE.lower() == 'pickle'):
			self.mapFacade = MapPickleFacade()
		
		self.rescan()
	
	def rescan(self):
		''' Rescan map directory for maps.
			
			Start fresh and load map data.
		'''
		self.availableMaps = []
		
		print("ext=%s"%self.mapFacade.extension)
		
		for f in os.listdir(MAP_PATH):
			print("Checking %s"%f)
			print("  %s"%os.path.splitext(f)[1])
			if (not f.startswith('.') and os.path.splitext(f)[1].lstrip('.') == self.mapFacade.extension):
				print("  adding %s"%f)
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
		return self.mapFacade.load(filename)
		
	def writeMap(self, map, filename):
		self.mapFacade.write(map, filename)
		
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


class MapXMLFacade(object):
	def __init__(self):
		self.extension = 'xmap'
	
	def load(self, filename):
		fh = open("%s%s"%(MAP_PATH,filename),'r')
		
		p = xml.sax.make_parser()
		mp = XMLMapParser()
		p.setContentHandler(mp)
		
		p.parse(fh)
		
		return mp.map
	
	def loadAsString(self, filename):
		fullPath = "%s%s"%(MAP_PATH,filename)
		m = None
		
		if (os.path.exists(fullPath)):
			try:
				fh = open(fullPath, 'r')
			except IOError as (errno, strerror):
				LOG.error("Could not open file: %s [%s]"%(fullPath,strerror))
			else:
				fh.close()
		else:
			LOG.error("Map file does not exist: %s"%(file))
		
		return m
	
	def write(self, map, filename):
		pass
	
class MapPickleFacade(object):
	def __init__(self):
		self.extension = 'map'
	
	def load(self, filename):
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

	def loadAsString(self, filename):
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

	def write(self, map, filename):
		fullPath = "%s%s"%(MAP_PATH,filename)
		
		try:
			fh = open(fullPath, 'wb')
			try:
				cPickle.dump(map,fh,2)
			except cPickle.PicklingError as (errno, strerror):
				LOG.error("Could not write file: %s [%s]"%(fullPath,strerror))
		except IOError as (errno, strerror):
			LOG.error("Could not open file: %s [%s]"%(fullPath,strerror))
		else:
			fh.close()

class XMLMapParser(xml.sax.ContentHandler):
	def startDocument(self):
		self.map           = Map()
		
		self.currentObject = None
		
		# Map variables
		self.mapName       = ""
		self.mapNumplayers = ""
		# Player variables
		self.playerType      = ''
		self.playerFaction   = ''
		self.playerAI        = ''
		# Entity Variables
		self.entityX         = ''
		self.entityY         = ''
		self.entityZ         = ''
		self.entityH         = ''
		self.entityP         = ''
		self.entityR         = ''
		self.entityOwnerId   = ''
		self.entityType      = ''
		self.entityModel     = ''
		self.entityMoveRad   = ''
		self.entityAttackRad = ''
		self.entitySensorRad = ''
		self.entityFuel      = ''
		self.entityCost      = ''
		self.entityMovedS    = ''
		self.entityAttactedS = ''
		# Camera variables
		self.cameraPosX      = ''
		self.cameraPosY      = ''
		self.cameraPosZ      = ''
		self.cameraLookX     = ''
		self.cameraLookY     = ''
		self.cameraLookZ     = ''
		self.cameraTargetX   = ''
		self.cameraTargetY   = ''
		self.cameraTargetZ   = ''
		self.cameraFOV       = ''
		self.cameraDist      = ''
		self.skyboxModel     = ''
		self.skyboxTex1File  = ''
		self.skyboxTex1Sort  = ''
		self.skyboxTex2File  = ''
		self.skyboxTex2Sort  = ''
		self.skyboxShader    = ''
		
		# State variables
		self.isMapEl           = False
		self.isMapNameEl       = False
		self.isMapNumplayersEl = False
		self.isPlayerEl        = False
		self.isPlayerTypeEl    = False
		self.isPlayerFactionEl = False
		self.isPlayerAiEl      = False
		self.isEntityEl        = False
		self.isEntityTypeEl    = False
		self.isEntityModelEl   = False
		self.isEntityMoveREl   = False
		self.isEntityAttackREl = False
		self.isEntitySensorREl = False
		self.isEntityFuelEl    = False
		self.isEntityCostEl    = False
		self.isCameraEl        = False
		self.isCameraFOVEl     = False
		self.isCameraDistEl    = False
		self.isSkyboxEl        = False
		self.isSkyboxModelEl   = False
		self.isSkyboxTex1El    = False
		self.isSkyboxTex2El    = False
		self.isSkyboxShaderEl  = False
		self.isLightEl         = False
				
		# Stat variables
		self.playerCount = 0
		self.entityCount = 0
		self.skyboxCount = 0
		self.cameraCount = 0
		self.lightCount  = 0
		
	def startElement(self, tag, attributes):
		# Entity tags
		if tag == 'entity':
			self.isEntityEl = True
			self.entityCount += 1
		elif tag == 'type' and self.isEntityEl:
			self.isEntityTypeEl = True
		elif tag == 'position' and self.isEntityEl:
			self.entityX = attributes.get('x')
			self.entityY = attributes.get('y')
			self.entityZ = attributes.get('z')
		elif tag == 'hpr' and self.isEntityEl:
			self.entityH = attributes.get('h')
			self.entityP = attributes.get('p')
			self.entityR = attributes.get('r')
		elif tag == 'owner' and self.isEntityEl:
			self.entityOwnerId = attributes.get('id')
		elif tag == 'model' and self.isEntityEl:
			self.isEntityModelEl = True
		elif tag == 'moveRad' and self.isEntityEl:
			self.isEntityMoveREl = True
		elif tag == 'attackRad' and self.isEntityEl:
			self.isEntityAttackREl = True
		elif tag == 'sensorRad' and self.isEntityEl:
			self.isEntitySensorREl = True
		elif tag == 'fuel' and self.isEntityEl:
			self.isEntityFuelEl = True
		elif tag == 'cost' and self.isEntityEl:
			self.isEntityCostEl = True
		elif tag == 'moved' and self.isEntityEl:
			self.entityMovedS = attributes.get('s')
		elif tag == 'attacked' and self.isEntityEl:
			self.entityAttackedS = attributes.get('s')
		# Player tags
		elif tag == 'player':
			self.isPlayerEl = True
			id   = attributes.get('id')
			self.currentObject = Player(id=id)
			self.playerCount += 1
		elif tag == 'type' and self.isPlayerEl:
			self.isPlayerTypeEl = True
		elif tag == 'faction' and self.isPlayerEl:
			self.isPlayerFactionEl = True
		elif tag == 'ai' and self.isPlayerEl:
			self.isPlayerAiEl = True
		# Camera tags
		elif tag == 'camera':
			self.isCameraEl = True
			self.cameraCount += 1
		elif tag == 'fov' and self.isCameraEl:
			self.isCameraFOVEl = True
		elif tag == 'position' and self.isCameraEl:
			self.cameraPosX = attributes.get('x')
			self.cameraPosY = attributes.get('y')
			self.cameraPosZ = attributes.get('z')
		elif tag == 'lookat' and self.isCameraEl:
			self.cameraLookX = attributes.get('x')
			self.cameraLookY = attributes.get('y')
			self.cameraLookZ = attributes.get('z')
		elif tag == 'target' and self.isCameraEl:
			self.cameraTargetX = attributes.get('x')
			self.cameraTargetY = attributes.get('y')
			self.cameraTargetZ = attributes.get('z')
		elif tag == 'distance' and self.isCameraEl:
			self.isCameraDistEl = True
		# Skybox tags
		elif tag == 'skybox':
			print("found skybox")
			self.isSkyboxEl = True
			self.skyboxCount += 1
		elif tag == 'model' and self.isSkyboxEl:
			print("found model")
			self.isSkyboxModelEl = True
		elif tag == 'texture' and self.isSkyboxEl:
			print("found texture, stage=%s"%attributes.get('stage'))
			if attributes.get('stage') == 'Space':
				self.isSkyboxTex1El = True
				self.skyboxTex1Sort = int(attributes.get('sort'))
				print("  found skyboxTex1Sort=%s"%self.skyboxTex1Sort)
			if attributes.get('stage') == 'SpaceClouds':
				self.isSkyboxTex2El = True
				self.skyboxTex2Sort = int(attributes.get('sort'))
				print("  found skyboxTex2Sort=%s"%self.skyboxTex2Sort)
		elif tag == 'shader' and self.isSkyboxEl:
			self.isSkyboxShaderEl = True
		# Light tags
		elif tag == 'light':
			self.isLightEl = True
			self.lightCount += 1
			type = attributes.get('type')
			tag  = attributes.get('tag')
			self.currentObject = {'type':type, 'tag':tag, 'color':None, 'hpr':None, 'pos':None}
		elif tag == 'color' and self.isLightEl:
			r = float(attributes.get('r'))
			g = float(attributes.get('g'))
			b = float(attributes.get('b'))
			a = float(attributes.get('a'))
			self.currentObject['color'] = (r,g,b,a)
		elif tag == 'hpr' and self.isLightEl:
			h = float(attributes.get('h'))
			p = float(attributes.get('p'))
			r = float(attributes.get('r'))
			self.currentObject['hpr'] = (h,p,r)
		elif tag == 'position' and self.isLightEl:
			x = float(attributes.get('x'))
			y = float(attributes.get('y'))
			z = float(attributes.get('z'))
			self.currentObject['pos'] = (x,y,z)
		# Map tags
		elif tag == 'map':
			self.isMapEl = True
			self.map.VERSION = attributes.get('version')
			self.map.id = int(attributes.get('id'))
		elif tag == 'name' and self.isMapEl:
			self.isMapNameEl = True
		elif tag == 'size' and self.isMapEl:
			x = float(attributes.get('x'))
			y = float(attributes.get('y'))
			z = float(attributes.get('z'))
			self.map.mapSize = (x,y,z)
		elif tag == 'numplayers' and self.isMapEl:
			self.isMapNumplayersEl = True
			
	def characters(self, ch):
		# Entity characters
		if self.isEntityTypeEl:
			self.entityType += ch
		elif self.isEntityModelEl:
			self.entityModel += ch
		elif self.isEntityMoveREl:
			self.entityMoveRad += ch
		elif self.isEntityAttackREl:
			self.entityAttackRad += ch
		elif self.isEntitySensorREl:
			self.entitySensorRad += ch
		elif self.isEntityFuelEl:
			self.entityFuel += ch
		elif self.isEntityCostEl:
			self.entityCost += ch
		# Player characters
		elif self.isPlayerTypeEl:
			self.playerType += ch
		elif self.isPlayerFactionEl:
			self.playerFaction += ch
		# Map characters
		elif self.isMapNameEl:
			self.mapName += ch
		elif self.isMapNumplayersEl:
			self.mapNumplayers += ch
		# Camera characters
		elif self.isCameraFOVEl:
			self.cameraFOV += ch
		elif self.isCameraDistEl:
			self.cameraDist += ch
		# Skybox characters
		elif self.isSkyboxModelEl:
			self.skyboxModel += ch
		elif self.isSkyboxTex1El:
			self.skyboxTex1File += ch
		elif self.isSkyboxTex2El:
			self.skyboxTex2File += ch
		elif self.isSkyboxShaderEl:
			self.skyboxShader += ch
		# No Light Characters
		
	def endElement(self, tag):
		# Entity tags
		if tag == 'entity':
			# TODO: link with owner
			entityClass = getattr(Entity, "Entity"+self.entityType)
			entity = entityClass()
			entity.pos       = (float(self.entityX), float(self.entityY), float(self.entityZ))
			entity.hpr       = (float(self.entityH), float(self.entityP), float(self.entityR))
			entity.modelFile = self.entityModel
			entity.moveRad   = int(self.entityMoveRad)
			entity.attackRad = int(self.entityAttackRad)
			entity.sensorRad = int(self.entitySensorRad)
			entity.fuel      = self.entityFuel
			entity.cost      = self.entityCost
			print("   Built entity %s"%entity)
			self.entityX         = ''
			self.entityY         = ''
			self.entityZ         = ''
			self.entityH         = ''
			self.entityP         = ''
			self.entityR         = ''
			self.entityOwnerId   = ''
			self.entityType      = ''
			self.entityModel     = ''
			self.entityMoveRad   = ''
			self.entityAttackRad = ''
			self.entitySensorRad = ''
			self.entityFuel      = ''
			self.entityCost      = ''
			self.entityMovedS    = ''
			self.entityAttactedS = ''
			# TODO: handle states
			self.isEntityEl = False
			self.isMapEl    = True
			self.map.entityList.append(entity)
			self.currentObject = None
		if tag == 'type' and self.isEntityTypeEl:
			self.isEntityTypeEl = False
		if tag == 'model' and self.isEntityModelEl:
			self.isEntityModelEl = False
		if tag == 'moveRad' and self.isEntityMoveREl:
			self.isEntityMoveREl = False
		if tag == 'attackRad' and self.isEntityAttackREl:
			self.isEntityAttackREl = False
		if tag == 'sensorRad' and self.isEntitySensorREl:
			self.isEntitySensorREl = False
		if tag == 'fuel' and self.isEntityFuelEl:
			self.isEntityFuelEl = False
		if tag == 'cost' and self.isEntityCostEl:
			self.isEntityCostEl = False
		# Player tags
		if tag == 'player':
			self.isPlayerEl = False
			self.isMapEl    = True
			self.map.playerList.append(self.currentObject)
			self.currentObject = None
		elif tag == 'type' and self.isPlayerEl:
			self.isPlayerTypeEl = False
			self.currentObject.type = self.playerType
			self.playerType = ''
		elif tag == 'faction' and self.isPlayerEl:
			self.isPlayerFactionEl = False
			self.currentObject.faction = self.playerFaction
			self.playerFaction = ''
		elif tag == 'ai' and self.isPlayerEl:
			self.isPlayerAiEl = False
			self.currentObject.ai = self.playerAI
			self.playerAI = ''
		# Camera tags
		elif tag == 'camera' and self.isCameraEl:
			self.isCameraEl = False
			print("   fov=%s"%self.cameraFOV)
			print("   pos=(%s,%s,%s)"%(self.cameraPosX,self.cameraPosY,self.cameraPosZ))
			print("   lookAt=(%s,%s,%s)"%(self.cameraLookX,self.cameraLookY,self.cameraLookZ))
			print("   target=(%s,%s,%s)"%(self.cameraTargetX,self.cameraTargetY,self.cameraTargetZ))
			print("   camDist=%s"%self.cameraDist)
			c = CameraManager(fov=float(self.cameraFOV),
							  pos=(float(self.cameraPosX),float(self.cameraPosY),float(self.cameraPosZ)),
							  lookAt=(float(self.cameraLookX),float(self.cameraLookY),float(self.cameraLookZ)),
							  target=(float(self.cameraTargetX),float(self.cameraTargetY),float(self.cameraTargetZ)),
							  dist=float(self.cameraDist))
			self.map.cameraList.append(c)
			self.cameraPosX      = ''
			self.cameraPosY      = ''
			self.cameraPosZ      = ''
			self.cameraLookX     = ''
			self.cameraLookY     = ''
			self.cameraLookZ     = ''
			self.cameraTargetX   = ''
			self.cameraTargetY   = ''
			self.cameraTargetZ   = ''
			self.cameraFOV       = ''
			self.cameraDist      = ''
		elif tag == 'fov' and self.isCameraFOVEl:
			self.isCameraFOVEl = False
		elif tag == 'distance' and self.isCameraDistEl:
			self.isCameraDistEl = False
		# Skybox tags
		elif tag == 'skybox':
			self.isSkyboxEl == False
			print("tex1 = %s"%self.skyboxTex1File)
			
			s = SkyBox(None,
					   modelFile=self.skyboxModel,
					   shaderFile=self.skyboxShader,
					   texture1File=self.skyboxTex1File,
					   texture2File=self.skyboxTex2File,
					   texture1Sort=self.skyboxTex1Sort,
					   texture2Sort=self.skyboxTex2Sort)
			self.map.skybox = s
		elif tag == 'model' and self.isSkyboxEl:
			self.isSkyboxModelEl = False
		elif tag == 'texture' and self.isSkyboxEl:
			# It's easier to switch both texture states off rather than
			# determine which one we're in
			self.isSkyboxTex1El = False
			self.isSkyboxTex2El = False
		elif tag == 'shader' and self.isSkyboxEl:
			self.isSkyboxShaderEl = False
		# Light tags
		elif tag == 'light' and self.isLightEl:
			self.isLightEl = False
			self.map.lightList.append(self.currentObject)
			self.currentObject = {'type':type, 'tag':tag, 'color':None, 'hpr':None, 'pos':None}
		# Map tags
		elif tag == 'map':
			self.isMapEl    = False
		elif tag == 'name' and self.isMapNameEl:
			self.map.name = self.mapName
			self.isMapNameEl = False
			self.mapName = ''
		elif tag == 'numplayers' and self.isMapNumplayersEl:
			self.map.numPlayers = int(self.mapNumplayers)
			self.isMapNumplayersEl = False
			self.mapNumplayers = ''
			
	def endDocument(self):
		#global mapFile
		#print("Parsing done:")
		#print("Name=%s, id=%d, version=%s, size=%s, numplayers=%s"%(self.map.name, self.map.id, self.map.VERSION, self.map.mapSize, self.mapNumplayers))
		#print("  Parsed %d players, created %d players"%(self.playerCount, len(self.map.playerList)))
		#print("  Parsed %d entities, created %d entities"%(self.entityCount, len(self.map.entityList)))
		#print("  Parsed %d cameras, created %d cameras"%(self.cameraCount, len(self.map.cameraList)))
		#print("  Parsed %d skybox, created %s"%(self.skyboxCount, self.map.skybox))
		#print("  Parsed %d lights, created %d"%(self.lightCount, len(self.map.lightList)))
		#print("    %s"%self.map.lightList)
		
		#file = os.path.splitext(mapFile)[0]
		#fullPath = "%s%s%s"%(MAP_PATH, file, MAP_EXT)
		#print("Saving map to %s"%(fullPath))
		
		#try:
		#	fh = open(fullPath, 'wb')
		#	try:
		#		cPickle.dump(self.map,fh,2)
		#	except cPickle.PicklingError as (err):
		#		LOG.error("Could not write file: %s [%s]"%(fullPath,err))
		#except IOError as (errno, strerror):
		#	LOG.error("Could not open file: %s [%s]"%(fullPath,strerror))
		#else:
		#	fh.close()
		pass