''' Grid.py
	
	Games space grid. This is no longer used.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			
'''

# Panda imports
from pandac.PandaModules import CollisionHandlerQueue
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionRay
from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import Geom
from pandac.PandaModules import GeomNode
from pandac.PandaModules import GeomTriangles
from pandac.PandaModules import GeomVertexData
from pandac.PandaModules import GeomVertexFormat
from pandac.PandaModules import GeomVertexWriter
from pandac.PandaModules import LineSegs
from pandac.PandaModules import NodePath
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4

# PSG imports
from game import Event
from game.GameConsts import *
from game.Util import frange

# Creates the grid overlay for the Universe.
# Grid implementation adapted from http://www.panda3d.org/phpbb2/viewtopic.php?t=3034
class Grid(object):
	'''The grid object draws a bunch of lines and flattens them into a single
	   object.'''
	def __init__(self, parent, boardRad, gridInt):
		Event.Dispatcher().register(self, 'E_Key_GridUp', self.gridMove)
		Event.Dispatcher().register(self, 'E_Key_GridDown', self.gridMove)
		
		self.currZ = 0
		self.gridInt = gridInt
		self.boardRad = boardRad
		
		if((boardRad*2) % gridInt is not 0):
			print("ERROR: gridInt can not fit in universeRadius")
			Event.Dispatcher().broadcast(Event.Event('E_ExitGame', src=self))
		
		self.gridNP = NodePath("Grid Node Parent")
		self.squareNP = NodePath("Squares Node Parent")
		
		'''
		#Since we are using collision detection to do picking, we set it up like
		#any other collision detection system with a traverser and a handler
		self.picker = CollisionTraverser()            #Make a traverser
		self.pq     = CollisionHandlerQueue()         #Make a handler
		#Make a collision node for our picker ray
		self.pickerNode = CollisionNode('mouseRay')
		#Attach that node to the camera since the ray will need to be positioned
		#relative to it
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		#Everything to be picked will use bit 1. This way if we were doing other
		#collision we could seperate it
		self.pickerNode.setFromCollideMask(BitMask32.bit(1))
		self.pickerRay = CollisionRay()               #Make our ray
		self.pickerNode.addSolid(self.pickerRay)      #Add it to the collision node
		#Register the ray as something that can cause collisions
		self.picker.addCollider(self.pickerNP, self.pq)
		#self.picker.showCollisions(render)
		'''
			
		# Draw centered lines
		self.drawLine(self.gridNP, Vec3(0, -boardRad, self.currZ), Vec3(0, boardRad, self.currZ))
		self.drawLine(self.gridNP, Vec3(-boardRad, 0, self.currZ), Vec3(boardRad, 0, self.currZ))
		# Draw lines in y-axis direction
		for x in frange(gridInt, (boardRad + gridInt), gridInt):
			self.drawLine(self.gridNP, Vec3(x, -boardRad, self.currZ), Vec3(x, boardRad, self.currZ))
			self.drawLine(self.gridNP, Vec3(-x, -boardRad, self.currZ), Vec3(-x, boardRad, self.currZ))
		# Draw lines in x-axis direction
		for y in frange(gridInt, (boardRad + gridInt), gridInt):
			self.drawLine(self.gridNP, Vec3(-boardRad, y, self.currZ), Vec3(boardRad, y, self.currZ))
			self.drawLine(self.gridNP, Vec3(-boardRad, -y, self.currZ), Vec3(boardRad, -y, self.currZ))
			
		self.gridNP.flattenStrong()
		# Start with grids turned off
		#self.gridNP.hide()
		
		self.gridNP.reparentTo(parent)
		
	# drawLine
	# Draws a line from source to target and parents to parent
	def drawLine(self, parent, source, target):
		line = LineSegs()
		line.setThickness(LINETHICKNESS)
		line.reset()
		line.setColor(*GRIDCOLOR)
		line.moveTo(source)
		line.drawTo(target)
		node = line.create()
		lineSegNP = NodePath(node).reparentTo(parent)
	
	# drawSquare
	# Draws a square from ll (x1, y2, z1) to ur (x2, y2, z2) returns a node path
	def drawSquare(self, x1,y1,z1, x2,y2,z2):
		format=GeomVertexFormat.getV3n3cpt2()
		vdata=GeomVertexData('square', format, Geom.UHStatic)
		
		vertex=GeomVertexWriter(vdata, 'vertex')
		normal=GeomVertexWriter(vdata, 'normal')
		color=GeomVertexWriter(vdata, 'color')
		texcoord=GeomVertexWriter(vdata, 'texcoord')
		
		#make sure we draw the sqaure in the right plane
		#if x1!=x2:
		vertex.addData3f(x1, y1, z1)
		vertex.addData3f(x2, y1, z1)
		vertex.addData3f(x2, y2, z2)
		vertex.addData3f(x1, y2, z2)

		normal.addData3f(self.myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z1-1)))
		normal.addData3f(self.myNormalize(Vec3(2*x2-1, 2*y1-1, 2*z1-1)))
		normal.addData3f(self.myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z2-1)))
		normal.addData3f(self.myNormalize(Vec3(2*x1-1, 2*y2-1, 2*z2-1)))
		
		#adding different colors to the vertex for visibility
		color.addData4f(0.0,0.5,0.0,0.5)
		color.addData4f(0.0,0.5,0.0,0.5)
		color.addData4f(0.0,0.5,0.0,0.5)
		color.addData4f(0.0,0.5,0.0,0.5)
		
		texcoord.addData2f(0.0, 1.0)
		texcoord.addData2f(0.0, 0.0)
		texcoord.addData2f(1.0, 0.0)
		texcoord.addData2f(1.0, 1.0)

		#quads arent directly supported by the Geom interface
		#you might be interested in the CardMaker class if you are
		#interested in rectangle though
		tri1=GeomTriangles(Geom.UHStatic)
		tri2=GeomTriangles(Geom.UHStatic)
		
		tri1.addVertex(0)
		tri1.addVertex(1)
		tri1.addVertex(3)
		
		tri2.addConsecutiveVertices(1,3)
		
		tri1.closePrimitive()
		tri2.closePrimitive()
		
		square=Geom(vdata)
		square.addPrimitive(tri1)
		square.addPrimitive(tri2)
		#square.setIntoCollideMask(BitMask32.bit(1))
		
		squareNP = NodePath(GeomNode('square gnode')) 
		squareNP.node().addGeom(square)
		squareNP.setTransparency(1) 
		squareNP.setAlphaScale(.5) 
		squareNP.setTwoSided(True)
		squareNP.setCollideMask(BitMask32.bit(1))
		return squareNP
	
	# myNormalize
	# Calculates a normal (How?)
	def myNormalize(self, myVec):
		myVec.normalize()
		return myVec
	
	def gridMove(self, event):
		print("moving grid")
		if event.type == 'E_Key_GridUp':
			self.gridNP.setPos(self.gridNP.getX(), self.gridNP.getY(), self.currZ + self.gridInt)
		if event.type == 'E_Key_GridDown':
			self.gridNP.setPos(self.gridNP.getX(), self.gridNP.getY(), self.currZ - self.gridInt)
	
	# toggleState
	# Toggles between grid layers and grid off
	def toggleState(self):
		if (S.currLayer == 0):
			S.currLayer = 1
			self.gridNPList[0].show()
		elif(S.currLayer == universeLayers):
			self.gridNPList[S.currLayer-1].hide()
			S.currLayer = 0
		else:
			self.gridNPList[S.currLayer-1].hide()
			S.currLayer = S.currLayer + 1
			self.gridNPList[S.currLayer-1].show()
