''' GXO.py
	
	Graphics Object Library
	
	Author:			Chad Rempp
	Date:			2010/11/12
	License:		GNU LGPL v3 
'''
# Python imports
import math

# Panda imports
from pandac.PandaModules import BitMask32
from pandac.PandaModules import GraphicsOutput
from pandac.PandaModules import OrthographicLens
from pandac.PandaModules import PNMImage
from pandac.PandaModules import Point3
from pandac.PandaModules import Point2
from pandac.PandaModules import PointLight
from pandac.PandaModules import Texture
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import VBase3D
from pandac.PandaModules import Vec2
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4
from direct.task import Task

# PSG imports
from game.GXEng import GXMgr

class GXOBase(object):
	def __init__(self, parent=render, pos=Vec3(0,0,0)):
		self.parent   = parent
		self.basePos  = pos
		self.baseNode = parent.attachNewNode(self.__class__.__name__)
		
		self.baseNode.setPos(self.basePos)
		
	
class GXOStar(GXOBase):
	def __init__(self, parent=render, pos=Vec3(50,0,0)):
		GXOBase.__init__(self, parent, pos)
				
		self._initializeFlare()
	
	def _initializeFlare(self):
		# Parameters
		self.distance     = 130000.0
		self.threshold    = 0.3
		self.radius       = 0.8
		self.strength     = 1.0
		self.suncolor     = Vec4( 1, 1, 1, 1 )
		self.suncardcolor = Vec4( 1, 1, 0, 0 )
		
		# Initialize some values
		self.obscured = 0.0
		
		# flaredata will hold the rendered image 
		self.flaredata = PNMImage()
		# flaretexture will store the rendered buffer
		self.flaretexture = Texture()
		
		# Create a 10x10 texture buffer for the flare
		self.flarebuffer = base.win.makeTextureBuffer("Flare Buffer", 10, 10)
		# Attach the texture to the buffer
		self.flarebuffer.addRenderTexture(self.flaretexture, GraphicsOutput.RTMCopyRam)
		self.flarebuffer.setSort(-100)
		
		# Camera that renders the flare buffer
		self.flarecamera = base.makeCamera(self.flarebuffer)
		#self.flarecamera.reparentTo(base.cam)
		#self.flarecamera.setPos(-50,0,0)
		self.ortlens = OrthographicLens()
		self.ortlens.setFilmSize(10, 10) # or whatever is appropriate for your scene
		self.ortlens.setNearFar(1,self.distance)
		self.flarecamera.node().setLens(self.ortlens)
		self.flarecamera.node().setCameraMask(GXMgr.MASK_GXM_HIDDEN)
		
		# Create a light for the flare
		self.sunlight = self.baseNode.attachNewNode(PointLight("Sun:Point Light"))
		self.sunlight.node().setColor(self.suncolor)
		self.sunlight.node().setAttenuation(Vec3( 0.1, 0.04, 0.0 ))
		
		# Load texture cards
		# Create a nodepath that'll hold the texture cards for the new lens-flare
		self.texcardNP = aspect2d.attachNewNode('Sun:flareNode1')
		self.texcardNP.attachNewNode('Sun:fakeHdr')
		self.texcardNP.attachNewNode('Sun:starburstNode')
		# Load a circle and assign it a color. This will be used to calculate
		# Flare occlusion
		self.starcard = loader.loadModel('../data/models/unitcircle.egg')
		self.starcard.reparentTo(self.baseNode)
		self.starcard.setColor(self.suncardcolor)
		self.starcard.setScale(1)
		#self.starcard.setTransparency(TransparencyAttrib.MAlpha)
		# This is necessary since a billboard always rotates the y-axis to the
		# target but we need the z-axis
		self.starcard.setP(-90)
		self.starcard.setBillboardPointEye(self.flarecamera, 0.0)
		# Don't let the main camera see the star card
		self.starcard.show(GXMgr.MASK_GXM_HIDDEN)
		self.starcard.hide(GXMgr.MASK_GXM_VISIBLE)
		
		#the models are really just texture cards create with egg-texture-cards
		# from the actual pictures
		self.hdr = loader.loadModel('../data/models/fx_flare.egg')
		self.hdr.reparentTo(self.texcardNP.find('**/Sun:fakeHdr'))
		
		# Flare specs
		self.starburst_0 = loader.loadModel('../data/models/fx_starburst_01.egg')
		self.starburst_1 = loader.loadModel('../data/models/fx_starburst_02.egg')
		self.starburst_2 = loader.loadModel('../data/models/fx_starburst_03.egg')
		self.starburst_0.setPos(0.5,0,0.5)
		self.starburst_1.setPos(0.5,0,0.5)
		self.starburst_2.setPos(0.5,0,0.5)
		self.starburst_0.setScale(.2)
		self.starburst_1.setScale(.2)
		self.starburst_2.setScale(.2)
		self.starburst_0.reparentTo(self.texcardNP.find('**/Sun:starburstNode'))
		self.starburst_1.reparentTo(self.texcardNP.find('**/Sun:starburstNode'))
		self.starburst_2.reparentTo(self.texcardNP.find('**/Sun:starburstNode'))
		
		self.texcardNP.setTransparency(TransparencyAttrib.MAlpha)
		# Put the texture cards in the background bin
		self.texcardNP.setBin('background', 0)
		# The texture cards do not affect the depth buffer
		self.texcardNP.setDepthWrite(False)
		
		#attach a node to the screen middle, used for some math
		self.mid2d = aspect2d.attachNewNode('mid2d')
		
		#start the task that implements the lens-flare
		taskMgr.add(self._flareTask, 'Sun:flareTask')
		
	## this function returns the aspect2d position of a light source, if it enters the cameras field of view
	def _get2D(self, nodePath):
		#get the position of the light source relative to the cam
		p3d = base.cam.getRelativePoint(nodePath, Point3(0,0,0))
		p2d = Point2()
		
		#project the light source into the viewing plane and return 2d coordinates, if it is in the visible area(read: not behind the cam)
		if base.cam.node().getLens().project(p3d, p2d):
			return p2d
		
		return None

	def _getObscured(self, color):
		# This originally looked for the radius of the light but that caused
		# assertion errors. Now I use the radius of the hdr model.
		bounds = self.starcard.getBounds()
		#print ("bounds=%s rad=%s"%(bounds,bounds.getRadius()))
		if not bounds.isEmpty():
			r = bounds.getRadius()
			# Setting the film size sets the field-of-view and the aspect ratio
			# Maybe this should be done with setAspectRation() and setFov()
			self.ortlens.setFilmSize(r * self.radius, r * self.radius)
			
			# Point the flarecamera at the sun so we can determine if anything
			# is obscurring the sun
			self.flarecamera.lookAt(self.baseNode)
			
			# Renders the next frame in all the registered windows, and flips
			# all of the frame buffers. This will populate flaretexture since
			# it's attached to the flarebuffer.
			# Save the rendered frame in flaredata
			base.graphicsEngine.renderFrame()
			self.flaretexture.store(self.flaredata)
			
			#print ("flaredata=%s | color=%s"%(self.flaredata.getXel(5,5), color))
			
			# Initialize the obscured factor
			obscured = 100.0
			color = VBase3D(color[0],color[1],color[2])
			for x in xrange(0,9):
				for y in xrange(0,9):
					if color.almostEqual(self.flaredata.getXel(x,y), self.threshold):
						obscured -=  1.0
		else:
			obscured = 0
		return obscured
	
	
	def _flareTask(self, task):
		#going through the list of lightNodePaths
		#for index in xrange(0, len(self.lightNodes)):
			
		pos2d = self._get2D(self.sunlight)
		#if the light source is visible from the cam's point of view,
		# display the lens-flare
		if pos2d:
			#print ("Flare visible")
			
			# The the obscured factor
			obscured = self._getObscured(self.suncardcolor)
			# Scale it to [0,1]
			self.obscured = obscured/100
			##print obscured
			
			# Length is the length of the vector that goes from the screen
			# middle to the pos of the light. The length gets smaller the
			# closer the light is to the screen middle, however, since
			# length is used to calculate the brightness of the effect we
			# actually need an inverse behaviour, since the brightness
			# will be greates when center of screen= pos of light
			length = math.sqrt(pos2d.getX()*pos2d.getX()+pos2d.getY()*pos2d.getY())
			invLength= 1.0-length*2
			# Subtract the obscured factor from the inverted distence and
			# we have a value that simulates the power of the flare
			#brightness
			flarePower=invLength-self.obscured
			#print("light pos=%s | length=%s"%(pos2d,length))
			print("obs=%s | length=%s | inv=%s | pow=%s"%(self.obscured,length,invLength,flarePower))
			
			# Clamp the flare power to some values
			if flarePower < 0 and self.obscured > 0: flarePower = 0.0
			if flarePower < 0 and self.obscured <= 0: flarePower = 0.3
			if flarePower > 1  : flarePower = 1
			
			print("flarepower=%s"%(flarePower))
			
			#
			if self.obscured >= 0.8:
				self.texcardNP.find('**/Sun:starburstNode').hide()
			else:
				self.texcardNP.find('**/Sun:starburstNode').show()
				
				#drawing the lens-flare effect...
				r= self.suncolor.getX()
				g= self.suncolor.getY()
				b= self.suncolor.getZ()
				r = math.sqrt(r*r+length*length) * self.strength
				g = math.sqrt(g*g+length*length) * self.strength
				b = math.sqrt(b*b+length*length) * self.strength
				print("%s,%s,%s"%(r,g,b))
				
				# 
				if self.obscured > 0.19:
					a = self.obscured - 0.2
				else:
					a = 0.4 - flarePower
				
				#
				if a < 0 : a = 0
				if a > 0.8 : a = 0.8
				
				#
				self.hdr.setColor(r,g,b,0.8-a)
				self.hdr.setR(90*length)
				self.texcardNP.find('**/Sun:starburstNode').setColor(r,g,b,0.5+length)
				self.hdr.setPos(pos2d.getX(),0,pos2d.getY())
				self.hdr.setScale(8.5+(5*length))
				
				vecMid = Vec2(self.mid2d.getX(), self.mid2d.getZ())
				vec2d = Vec2(vecMid-pos2d)
				vec3d = Vec3(vec2d.getX(), 0, vec2d.getY())
				
				self.starburst_0.setPos(self.hdr.getPos()-(vec3d*10))
				self.starburst_1.setPos(self.hdr.getPos()-(vec3d*5))
				self.starburst_2.setPos(self.hdr.getPos()-(vec3d*10))
				self.texcardNP.show()
				#print "a",a
		else:
			#hide the lens-flare effect for a light source, if it is not visible...
			self.texcardNP.hide()
			
		return Task.cont