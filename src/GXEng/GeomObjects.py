''' GeomObjects.py
	
	A collection of geometry objects.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			
'''
# Python imports
from __future__ import division
import math

# Panda imports
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import BillboardEffect
from pandac.PandaModules import DepthTestAttrib
from pandac.PandaModules import Geom
from pandac.PandaModules import GeomTriangles
from pandac.PandaModules import GeomVertexData
from pandac.PandaModules import GeomVertexFormat
from pandac.PandaModules import GeomVertexWriter
from pandac.PandaModules import LineSegs
from pandac.PandaModules import NodePath
from pandac.PandaModules import RenderAttrib
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4
from pandac.PandaModules import GeomNode
from pandac.PandaModules import Plane
from pandac.PandaModules import Point3

# PSG imports
import Event
from Settings import GameSettings
from GSEng import Entity

class CircleBB(object):
	_EDGES = 40
	_np = NodePath()
	def __init__(self, parent, pos=Vec3(0, 0, 0), size=1, color=Vec4(0, 0, 0, 1)):
		print("  Creating circle at " + str(pos))
		self.aaLevel= int(GameSettings().getSetting('ANTIALIAS'))
		self.pos = pos
		self.size = size
		self.color = color
		self._np = self.draw()
		self._np.setTwoSided(True)
		self._np.setTransparency(1)
		self._np.setAttrib(DepthTestAttrib.make(RenderAttrib.MNone))
		self._np.setEffect(BillboardEffect.makePointEye())
		if self.aaLevel > 0:
			self._np.setAntialias(AntialiasAttrib.MPolygon, self.aaLevel)
		self._np.reparentTo(parent)
		
	def draw(self):
		format=GeomVertexFormat.getV3n3cpt2()
		vdata=GeomVertexData('square', format, Geom.UHDynamic)
		vertex=GeomVertexWriter(vdata, 'vertex')
		normal=GeomVertexWriter(vdata, 'normal')
		color=GeomVertexWriter(vdata, 'color')
		circle=Geom(vdata)
		# Create vertices
		vertex.addData3f(self.pos)
		color.addData4f(self.color)
		for v in range(self._EDGES):
			x = self.pos.getX() + (self.size * math.cos((2*math.pi/self._EDGES)*v))
			y = self.pos.getY() + (self.size * math.sin((2*math.pi/self._EDGES)*v))
			z = self.pos.getZ()
			vertex.addData3f(x, y, z)
			color.addData4f(self.color)
		
		# Create triangles
		for t in range(self._EDGES):
			tri = GeomTriangles(Geom.UHDynamic)
			tri.addVertex(0)
			tri.addVertex(t+1)
			if (t+2) > self._EDGES:
				tri.addVertex(1)
			else:
				tri.addVertex(t+2)
			tri.closePrimitive()
			circle.addPrimitive(tri)
		
		gn = GeomNode('Circle')
		gn.addGeom(circle)
		np = NodePath(gn)
		np.setHpr(0, 90, 0)
		return np
		
	def removeNode(self):
		self._np.removeNode()
		
	def __del__(self):
		self.removeNode()

class SelectionIndicator(object):
	_np = NodePath()
	_currHpr = Vec3(0, 0, 0)
	_color=Vec4(0.3, 0.3, 0.8, 1)
	
	def __init__(self, parent, entity, size=1):
		self.entity = entity
		self.aaLevel= int(GameSettings().getSetting('ANTIALIAS'))
		self.pos = entity.pos
		self.size = size
		self._np = loader.loadModelCopy("data/models/ribbon.egg")
		self._np.setScale(10)
		self._np.setHpr(self._currHpr)
		self._np.setTwoSided(True)
		if self.aaLevel > 0:
			self._np.setAntialias(AntialiasAttrib.MLine, self.aaLevel)
		print(self._np)
		self._np.reparentTo(parent)
		taskMgr.add(self.rotate, 'Selection Rotation Task')
		
	def rotate(self, Task):
		self._currHpr.setX(self._currHpr.getX() + 0.1)
		self._np.setHpr(self._currHpr)
		return Task.cont
		
	def removeNode(self):
		taskMgr.remove('Selection Rotation Task')
		self._np.removeNode()
		
	def __del__(self):
		self.removeNode()
	
	
class MoveCursor(object):
	_EDGES = 40
	_zPos             = 0
	_movingUp         = False
	_movingDown       = False
	_color = Vec4(0.3, 0.3, 0.8, 1)
	_currentPos = Vec3(0, 0, 0)
	
	def __init__(self, parent, entity, foot=1):
		self.entity = entity
		self._moveRadCircleNP  = NodePath("Movement Radius Node")
		self._moveLine         = LineSegs()
		self._moveLineNP       = NodePath("Movement Direction Line Node")
		self._moveZLine        = LineSegs()
		self._moveZLineNP      = NodePath("Movement Z Line Node")
		self._moveZFootNP      = NodePath("Movement Z Foot Node")
		self._moveFootCircle   = LineSegs()
		self._moveFootCircleNP = NodePath("Movement Foot Circle Node")
		self._attackRadCircle  = LineSegs()
		self._attackRadCircleNP= NodePath("Attack Radius Node")
		self._np               = NodePath("Movement Node")
		self.attackables       = []
		Event.Dispatcher().register(self, 'E_Key_ZUp', self.onZChange)
		Event.Dispatcher().register(self, 'E_Key_ZDown', self.onZChange)
		Event.Dispatcher().register(self, 'E_Key_ZUp-up', self.onZChange)
		Event.Dispatcher().register(self, 'E_Key_ZDown-up', self.onZChange)
		self.aaLevel= int(GameSettings().getSetting('ANTIALIAS'))
		self.parent = parent
		self.start  = Vec3(0, 0, 0)
		self.moveRad = entity.moveRad
		self.footRad = foot
		self.attackRad = entity.attackRad
		self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
		self.draw()
		self._np.reparentTo(self.parent)
		if self.aaLevel > 0:
			self._np.setAntialias(AntialiasAttrib.MLine, self.aaLevel)
		taskMgr.add(self.updateMovePos, 'Movement Indicator Update Task')
		
	def draw(self):
		# Setup curr mouse pos in 3d space
		posXY = self.getMouseXY()
		x = posXY.getX()
		y = posXY.getY()
		z = 0
		
		# Draw movement radius
		moveRadLine = LineSegs()
		moveRadLine.setThickness(1)
		moveRadLine.setColor(self._color)
		moveRadLine.moveTo(self.moveRad, 0, 0)
		for i in range(self._EDGES + 1):
			newX = (self.moveRad * math.cos((2*math.pi/self._EDGES)*i))
			newY = (self.moveRad * math.sin((2*math.pi/self._EDGES)*i))
			moveRadLine.drawTo(newX, newY, 0)
		moveRadGeom = moveRadLine.create()
		self._moveRadCircleNP = NodePath(moveRadGeom)
		self._moveRadCircleNP.reparentTo(self._np)
		
		# Draw movement foot circle
		self._moveFootCircle.setThickness(1)
		self._moveFootCircle.setColor(self._color)
		self._moveFootCircle.moveTo(self.footRad, 0, 0)
		for i in range(self._EDGES):
			newX = (self.footRad * math.cos((2*math.pi/self._EDGES)*i))
			newY = (self.footRad * math.sin((2*math.pi/self._EDGES)*i))
			self._moveFootCircle.drawTo(newX, newY, 0)
		self._moveFootCircle.drawTo(self.footRad, 0, 0)
		moveFootCircleGeom = self._moveFootCircle.create()
		self._moveFootCircleNP = NodePath(moveFootCircleGeom)
		self._moveFootCircleNP.reparentTo(self._np)
		
		# Draw movement direction line
		self._moveLine.setThickness(1)
		self._moveLine.setColor(self._color)
		self._moveLine.moveTo(0, 0, 0)
		self._moveLine.drawTo(x, y, z) 
		moveLine = self._moveLine.create()
		self._moveLineNP = NodePath(moveLine)
		self._moveLineNP.reparentTo(self._np)
		
		# Draw Z line
		self._moveZLine.setThickness(1)
		self._moveZLine.setColor(self._color)
		self._moveZLine.moveTo(self.start)
		self._moveZLine.drawTo(x, y, z) 
		moveZLine = self._moveZLine.create()
		self._moveZLineNP = NodePath(moveZLine)
		self._moveZLineNP.reparentTo(self._np)
		
		# Draw Attack Radius
		self._attackRadCircle.setThickness(1)
		self._attackRadCircle.setColor(0.8, 0.0, 0.0, 1)
		self._attackRadCircle.moveTo(self.attackRad, 0, 0)
		for i in range(self._EDGES + 1):
			newX = (self.attackRad * math.cos((2*math.pi/self._EDGES)*i))
			newY = (self.attackRad * math.sin((2*math.pi/self._EDGES)*i))
			self._attackRadCircle.drawTo(newX, newY, 0)
		attackRadCircleGeom = self._attackRadCircle.create()
		self._attackRadCircleNP = NodePath(attackRadCircleGeom)
		self._attackRadCircleNP.reparentTo(self._np)
		
	def updateMovePos(self, Task):
		# endPos must be transformed in the the coord sys of the model
		m_pos = self.getMouseXY()
		if m_pos is not None:
			# Transform current mouse pos
			endPos = self.parent.getRelativePoint(render, m_pos)
			
			# Adjust Z coord if needed
			if self._movingUp:
				self._zPos += 0.1
			elif self._movingDown:
				self._zPos -= 0.1
			endPos.setZ(self._zPos)
			
			# Check if we're trying to move too far, if not update pos
			dist = math.sqrt(endPos.getX()**2 + endPos.getY()**2 + 2*(endPos.getZ()**2))
			if dist <= self.moveRad:
				self._moveLine.setVertex(1, endPos)
				self._moveFootCircleNP.setPos(endPos)
				self._moveZLine.setVertex(0, Point3(endPos.getX(), endPos.getY(), 0))
				self._moveZLine.setVertex(1, endPos)
				self._attackRadCircleNP.setPos(endPos)
				self._currentPos = render.getRelativePoint(self._np, endPos)
				
				# Check for attackable ships in range of current pos
				attackables = Entity.EntityManager().getEntitiesWithin(self._currentPos, self.attackRad)
				# Unhighlight ships no longer in range
				for e in self.attackables:
					if e not in attackables and isinstance(e, Entity.EntityShip):
						e.representation.unsetAttackable()
				# Highlight ships in range
				for e in attackables:
					if isinstance(e, Entity.EntityShip) and e != self.entity and e.owner != self.entity.owner:
						e.representation.setAttackable()
				self.attackables = attackables
		return Task.cont
		
	def onZChange(self, event):
		if event.type == 'E_Key_ZUp':
			self._movingDown = False
			self._movingUp = True
		if event.type == 'E_Key_ZDown':
			self._movingUp = False
			self._movingDown = True
		if event.type == 'E_Key_ZUp-up':
			self._movingUp = False
			self._movingDown = False
		if event.type == 'E_Key_ZDown-up':	
			self._movingUp = False
			self._movingDown = False
		
	def getMouseXY(self):
		# NOTE - this returns the mouse pos in the ships coord sys
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos3d = Point3()
			nearPoint = Point3()
			farPoint = Point3()
			base.camLens.extrude(mpos, nearPoint, farPoint)
			if self.plane.intersectsLine(pos3d,
				render.getRelativePoint(camera, nearPoint),
				render.getRelativePoint(camera, farPoint)): 
					#print("Mouse ray intersects ground plane at " + str(pos3d))
					return pos3d
		
	def getPosition(self):
		return self._currentPos
		
	def removeNode(self):
		taskMgr.remove('Movement Indicator Update Task')
		for e in self.attackables:
			if isinstance(e, Entity.EntityShip):
				e.representation.unsetAttackable()
		self._moveRadCircleNP.removeNode()
		self._moveLineNP.removeNode()
		self._moveZLineNP.removeNode()
		self._moveZFootNP.removeNode()
		self._moveFootCircleNP.removeNode()
		self._attackRadCircleNP.removeNode()
		self._np.removeNode()
		
	def __del__(self):
		# TODO - This isn't calling self.removeNode() correctly
		self._np.removeNode()

class AttackCursor(object):
	_EDGES = 40
	_color = Vec4(0.8, 0.3, 0.3, 1)
	
	def __init__(self, parent, entity, foot=1):
		self.entity = entity
		self.pos = entity.pos
		self.attackRad         = entity.attackRad
		self.footRad           = foot
		self._footCircle       = LineSegs()
		self._footCircleNP     = NodePath("Movement Foot Circle Node")
		self._attackRadCircle  = LineSegs()
		self._attackRadCircleNP= NodePath("Attack Radius Node")
		self._np               = NodePath("Movement Node")
		self.attackables       = Entity.EntityManager().getEntitiesWithin(self.pos, self.attackRad)
		
		for e in self.attackables:
			if isinstance(e, Entity.EntityShip) and e != self.entity and e.owner != self.entity.owner: 
				e.representation.setAttackable()
			
	def draw(self):
		# Draw attack radius
		attackRadLine = LineSegs()
		attackRadLine.setThickness(1)
		attackRadLine.setColor(self._color)
		attackRadLine.moveTo(self.attackRad, 0, 0)
		for i in range(self._EDGES + 1):
			newX = (self.attackRad * math.cos((2*math.pi/self._EDGES)*i))
			newY = (self.attackRad * math.sin((2*math.pi/self._EDGES)*i))
			attackRadLine.drawTo(newX, newY, 0)
		attackRadGeom = attackRadLine.create()
		self._attackRadCircleNP = NodePath(attackRadGeom)
		self._attackRadCircleNP.reparentTo(self._np)
		
		# Draw foot circle
		self._footCircle.setThickness(1)
		self._footCircle.setColor(self._color)
		self._footCircle.moveTo(self.footRad, 0, 0)
		for i in range(self._EDGES):
			newX = (self.footRad * math.cos((2*math.pi/self._EDGES)*i))
			newY = (self.footRad * math.sin((2*math.pi/self._EDGES)*i))
			self._footCircle.drawTo(newX, newY, 0)
		self._footCircle.drawTo(self.footRad, 0, 0)
		footCircleGeom = self._footCircle.create()
		self._footCircleNP = NodePath(footCircleGeom)
		self._footCircleNP.reparentTo(self._np)
		
	def removeNode(self):
		for e in self.attackables:
			if isinstance(e, Entity.EntityShip):
				e.representation.unsetAttackable()
		self._footCircleNP.removeNode()
		self._attackRadCircleNP.removeNode()
		self._np.removeNode()

	def __del__(self):
		self.removeNode()
