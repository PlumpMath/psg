''' Representation.py
	
	Graphical representations of the entity objects.
	
	Each entity has a corresponding representation. The representation class
	that is instantiated is determined by the name of the entity class. For
	example, if the GSEng asks for a representation for an EntityLightCapture
	class a RepresentationLightCapture intance will be returned. For this
	reason the representation class names must match the entity class names.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			
'''

# Panda imports
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import NodePath
from pandac.PandaModules import Point3
from pandac.PandaModules import TextureStage
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4

# PSG imports
from game import Event
from game.Settings import GameSettings
from game.GSEng import Entity
#from game.GXEng import View
from game.GXEng import GeomObjects

class Representation(object):
	'''An abstract class that represents any logical entity in the game.'''
	pos = Vec3(0, 0, 0)
	hpr = Vec3(0, 0, 0)
	model = None
	tag = ""
	entity = None
	foot    = 10
	aaLevel = 2
	
	def __init__(self,  entity=None, pos=None,  hpr=None,  tag="", model=''):
		self.entity = entity
		if self.entity != None:
			self.pos = self.entity.getPos()
			self.hpr = self.entity.getHpr()
			self.tag = self.entity.getTag()
		if pos != None:
			self.pos = pos
		if hpr != None:
			self.hpr = hpr
		if tag != "":
			self.tag = tag
		self.aaLevel = int(GameSettings().antiAlias)
			
	def getPos(self):
		return self.pos
		
	def setModel(self, model):
		self.model = model
		
	def setPos(self, pos):
		self.pos = pos
		
	def setHpr(self, hpr):
		self.hpr = hpr
		
	def getTag(self):
		return self.tag
		
	def select(self):
		'''Must be subclassed'''
		pass
		
	def __repr__(self):
		return "<Rep: " + self.tag + ", pos=" + str(self.pos) + ">"
	
class RepShip(Representation):
	_selectindicator = None
	_movecursor = None
	_attackcursor = None
	
	def __init__(self, entity=None, pos=None,  hpr=None,  tag="", model=''):
		Representation.__init__(self, entity, pos,  hpr, tag, model)
		#super(Representation,self).__init__(self, entity, pos,  hpr,  tag, model)
		
	def selectMove(self):
		LOG.debug("[RepShip] Drawing move selector")
		# Draw movement radii
		self._selectindicator = GeomObjects.SelectionIndicator(self.model, size=self.foot)
		self._movecursor   = GeomObjects.MoveCursor(self.model, self.entity, foot=self.foot)
		
	def unselectMove(self):
		if self._selectindicator is not None:
			self._selectindicator.removeNode()
		if self._movecursor is not None:
			self._movecursor.removeNode()
		del(self._selectindicator)
		del(self._movecursor)
		
	def selectAttack(self):
		self._attackcursor = GeomObjects.AttackCursor(self.model, self.entity, foot=self.foot)
		
	def unselectAttack(self):
		if self._attackcursor is not None:
			self._attackcursor.removeNode()
		del(self._attackcursor)
		
	def setAttackable(self):
		self.model.setColor(0.8, 0, 0, 1)
		
	def unsetAttackable(self):
		self.model.setColorOff()
		
	def move(self, pos):
		# Get direction to head
		currentHpr = self.model.getHpr()
		self.model.lookAt(pos.getX(), pos.getY(), pos.getZ())
		targetHpr = self.model.getHpr()
		self.model.setHpr(currentHpr) 
		
		# Rotate to heading
		rot = LerpHprInterval(self.model, duration=1, hpr = targetHpr,
				other = None, blendType = 'easeInOut', bakeInStart = 1,
				fluid = 0, name = None)
		# Move
		mov = LerpPosInterval(self.model, duration=3,	pos = pos, #Vec3(10, 0, 0),
				startPos = None, other = None, blendType = 'easeInOut',
				bakeInStart = 1, fluid = 0,	name = None)
		# Level off (pitch = 0)
		lev = LerpHprInterval(self.model,	duration=0.7, hpr = Vec3(targetHpr.getX(), 0, 0),
				other = None, blendType = 'easeInOut', bakeInStart = 1,
				fluid = 0, name = None)
		moveSequence=Sequence(Func(self.fireEngines), rot, mov, lev, Func(self.killEngines))
		moveSequence.start()
		self.pos = pos
		
class RepLightCapture(RepShip):
	def __init__(self, entity=None, pos=None,  hpr=None,  tag="", model=''):
		RepShip.__init__(self, entity, pos, hpr, tag, model)
		#super(RepLightCapture,self).__init__(self, entity, pos,  hpr,  tag, model)
		self.model = loader.loadModelCopy("data/models/ship_03.egg")
		self.model.setScale(0.5)
		self.model.setPos(self.pos)
		self.model.setHpr(self.hpr)
		self.model.setTag('SelectorTag', self.tag)
		if self.aaLevel > 0:
			self.model.setAntialias(AntialiasAttrib.MMultisample, self.aaLevel)
		self.model.reparentTo(render)
		
	def fireEngines(self):
		pass
		
	def killEngines(self):
		pass
	
	def fireRockets(self, target):
		print("FIRING ROCKETS!!!")
		self.modelRocket = loader.loadModelCopy("data/models/rocket.egg")
		self.modelRocket.setScale(1)
		self.modelRocket.setPos(0, 0, 0)
		currentHpr = self.model.getHpr()
		self.modelRocket.setHpr(currentHpr)
		self.modelRocket.reparentTo(self.model)
		targetPos = self.model.getRelativePoint(render, target)
		
		#targetHpr = self.model.getHpr()
		#self.model.setHpr(currentHpr) 
		mov = LerpPosInterval(self.modelRocket, duration=3,	pos = targetPos, #Vec3(10, 0, 0),
				startPos = None, other = None, blendType = 'easeInOut',
				bakeInStart = 1, fluid = 0,	name = None)
		moveSequence=Sequence(mov, Func(self.modelRocket.removeNode))
		moveSequence.start()
		
class RepPlanet(Representation):
	def __init__(self, entity=None, pos=None,  hpr=None,  tag="", model=''):
		Representation.__init__(self, entity, pos,  hpr, tag, model)
		#super(Representation,self).__init__(self, entity, pos,  hpr,  tag, model)
		
		self.model = loader.loadModelCopy("data/models/planet_01.egg")
		self.model.setTexture(loader.loadTexture('data/textures/tex_planet_01.png'), 1)
		self.model.setScale(2.5)
		self.model.setPos(self.pos)
		self.model.setHpr(self.hpr)
		self.model.setTag('CollisionTag', self.tag)
		if self.aaLevel > 0:
			self.model.setAntialias(AntialiasAttrib.MMultisample, self.aaLevel)
			#self.model.setAntialias(AntialiasAttrib.MLine)
		self.model.reparentTo(render)
		
	def select(self):
		# Draw movement radii
		self._foot = GeomObjects.Circle(self.model, size=self.foot, color=Vec4(0.1, 0.1, 0.7, 0))
		#self._moveRadCircle = GeomObjects.Circle(self.model, size=self.entity.moveRad, color=Vec4(0.1, 0.1, 0.7, 0))
		
	def unSelect(self):
		self._foot.removeNode()
		#self._moveRadCircle.removeNode()
