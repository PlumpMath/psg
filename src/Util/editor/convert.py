''' convert.py
	
	This script converts maps between XML and pickled formats
	
	The script is still a little rough around the edges, but it is continuing to
	evolve at a rapid pace.
	
	Author:			Chad Rempp
	Date:			2010/01/16
	License:		GNU LGPL v3 
'''
import sys
import os
import cPickle
import xml.sax

sys.path.append('../../../src')
from GameConsts import *
from GSEng.Player import Player
from GSEng.Map import Map
from GSEng import Entity
from GameConsts import *
from GXEng.CameraMgr import CameraManager
from GXEng.SkyBox import SkyBox

mapFile = ''

class MapParser(xml.sax.ContentHandler):
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
				self.skyboxTex1Sort = attributes.get('sort')
				print("  found skyboxTex1Sort=%s"%self.skyboxTex1Sort)
			if attributes.get('stage') == 'SpaceClouds':
				self.isSkyboxTex2El = True
				self.skyboxTex2Sort = attributes.get('sort')
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
					   texture1Sort=int(self.skyboxTex1Sort),
					   texture2Sort=int(self.skyboxTex2Sort))
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
		global mapFile
		print("Parsing done:")
		print("Name=%s, id=%d, version=%s, size=%s, numplayers=%s"%(self.map.name, self.map.id, self.map.VERSION, self.map.mapSize, self.mapNumplayers))
		print("  Parsed %d players, created %d players"%(self.playerCount, len(self.map.playerList)))
		print("  Parsed %d entities, created %d entities"%(self.entityCount, len(self.map.entityList)))
		print("  Parsed %d cameras, created %d cameras"%(self.cameraCount, len(self.map.cameraList)))
		print("  Parsed %d skybox, created %s"%(self.skyboxCount, self.map.skybox))
		print("  Parsed %d lights, created %d"%(self.lightCount, len(self.map.lightList)))
		print("    %s"%self.map.lightList)
		
		file = os.path.splitext(mapFile)[0]
		fullPath = "%s%s%s"%(MAP_PATH, file, MAP_EXT)
		print("Saving map to %s"%(fullPath))
		
		try:
			fh = open(fullPath, 'wb')
			try:
				cPickle.dump(self.map,fh,2)
			except cPickle.PicklingError as (err):
				LOG.error("Could not write file: %s [%s]"%(fullPath,err))
		except IOError as (errno, strerror):
			LOG.error("Could not open file: %s [%s]"%(fullPath,strerror))
		else:
			fh.close()
		
def runConvert():
	global mapFile
	import os
	import os.path
	mapfiles = filter(lambda x: os.path.splitext(x)[1] == '.xmap', os.listdir(MAP_PATH))
	print("Choose a map to convert:")
	for i,map in enumerate(mapfiles):
		print("[%d] %s"%(i,map))
	m = raw_input('>>')
	print("Parsing %s"%mapfiles[int(m)])
	
	p = xml.sax.make_parser()
	p.setContentHandler(MapParser())
	mapFile = mapfiles[int(m)]
	fh = open("%s%s"%(MAP_PATH,mapFile),'r')
	p.parse(fh)