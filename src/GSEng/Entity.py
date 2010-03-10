''' Entity.py
	
	The game Entity objects.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3 
	Todo:			
'''

# Python imports
import math

# Panda imports
from pandac.PandaModules import Vec3

# PSG imports
from Util.Singleton import Singleton
#from GXEng.GXMgr import GXMgr
import Event


class EntityManager(object):
	'''
		TODO - Document
	'''
	__metaclass__ = Singleton
	
	_entities = {}
	_gxmgr    = None
	
	def __init__(self):
		'''
			TODO - Document
		'''
		LOG.debug("[EntityManager] Initializing")
	
	def registerGXEng(self, gxmgr):
		'''
			TODO - Document
		'''
		LOG.debug("[EntityManager] Registering GXMgr")
		self._gxmgr = gxmgr
	
	def addEntity(self, entity):
		'''
			TODO - Document
		'''
		LOG.debug("[EntityManager] Adding entity %s - %d"%(entity,id(entity)))
		if not entity in self._entities.keys():
			self._entities[entity] = self._gxmgr.buildRepresentation(entity)
			
	def delEntity(self,  entity):
		'''TODO - Broadcast a del'''
		LOG.debug("[EntityManager] Deleting entity %s"%entity)
		try:
			self._entities.remove(entity)
		except:
			pass
			
	def getFromTag(self, tag):
		'''
			TODO - Document
		'''
		LOG.debug("[EntityManager] Getting entity from tag %s"%tag)
		for e in self._entities:
			if e.getTag() == tag:
				return e
		return None
		
	def getEntitiesWithin(self, pos, radius):
		'''
			TODO - Document
		'''
		LOG.debug("[EntityManager] Finding entities within %s of point %s"%(radius, pos))
		entityList = []
		px = pos.getX()
		py = pos.getY()
		pz = pos.getZ()
		for e in self._entities:
			ex = e.getPos().getX()
			ey = e.getPos().getY()
			ez = e.getPos().getZ()
			d = math.sqrt((px-ex)**2 + (py-ey)**2 + (pz-ez)**2)
			if (d <= radius):
				entityList.append(e)
		return entityList

class Entity(object):
	'''An abstract class that represents any logical entity in the game.'''
	pos = Vec3()
	hpr = Vec3()
	type = ""
	owner = None
	tag  = ""
	representation = None
	modelFile = ''
	
	def __init__(self,  pos=None,  hpr=None,  type="",  owner=None,  tag="", model=''):
		if pos != None:
			self.pos = pos
		if hpr != None:
			self.hpr = hpr
		if type != "":
			self.type = type
		if owner != None:
			self.owner = owner
		if tag != "":
			self.tag = tag
		self.modelFile = model
			
	def setOwner(self, owner):
		self.owner = owner
		
	def getTag(self):
		return self.tag
		
	def getPos(self):
		return self.pos
		
	def getHpr(self):
		return self.hpr
		
	def __repr__(self):
		return "<Entity: " + self.tag + ", pos=" + str(self.pos) + ">"
		
class EntityShip(Entity):
	'''Represents ship logic'''
	type = "SHIP"
	moveRad   = 0
	attackRad = 0
	sensorRad = 0
	fuel      = 0
	cost      = 0
	weaponList  = []
	abilityList = []
	representation = None
	moved = False
	attacked = False
			
	def __init__(self,  pos=None,  hpr=None,  type="",  owner=None,  tag=""):
		Entity.__init__(self, pos, hpr, type, owner, tag)
		
	def move(self,  newPos):
		self.pos = newPos
		self.representation.move(self.pos)
		
class EntityLightCapture(EntityShip):
	type = "SHIP"
	moveRad   = 1200 /10
	attackRad = 300 /10
	sensorRad = 800 /10
	fuel      = 99
	cost      = 1000
	weaponList  = []
	abilityList = []
	
	def __init__(self,  pos=None,  hpr=None,  type="",  owner=None,  tag=""):
		EntityShip.__init__(self, pos, hpr, type, owner, tag)
	
class EntityHeavyCapture(EntityShip):
	type = "SHIP"
	moveRad   = 1200 /10
	attackRad = 300 /10
	sensorRad = 800 /10
	fuel      = 70
	cost      = 3000
	weaponList  = []
	abilityList = []
	
	def __init__(self,  pos=None,  hpr=None,  type="",  owner=None,  tag=""):
		EntityShip.__init__(self, pos, hpr, type, owner, tag)
	
class EntityPlanet(Entity):
	'''Represents planet logic'''
	type = "Planet"
	
	def __init__(self,  pos=None,  hpr=None,  type="",  owner=None,  tag=""):
		Entity.__init__(self, pos, hpr, type, owner, tag)
