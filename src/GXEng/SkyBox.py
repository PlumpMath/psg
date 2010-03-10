''' SkyBox.py
	
	The sky box object
	
	Author:			Chad Rempp
	Date:			2009/12/12
	License:		GNU LGPL v3 
'''

# Python imports
#import os

# Panda imports
from direct.task import Task 
from pandac.PandaModules import DepthWriteAttrib
from pandac.PandaModules import Fog
from pandac.PandaModules import Shader
from pandac.PandaModules import Texture
from pandac.PandaModules import TextureStage
from pandac.PandaModules import Vec4

class SkyBox(object):
	'''
	
	'''
	
	def __init__(self, parent, modelFile='', shaderFile='', texture1File='', texture2File='', texture1Sort=0, texture2Sort=0):
		LOG.debug("[SkyBox] Initializing")
		self.modelFile    = modelFile
		self.shaderFile   = shaderFile
		self.texture1File = texture1File
		self.texture2File = texture2File
		self.texture1Sort = texture1Sort
		self.texture2Sort = texture2Sort
		self.parent       = parent
		
	def render(self):
		LOG.debug("[SkyBox] Rendering")
		
		# If we are an orphan use render
		if self.parent is None: self.parent = render
		
		#LOG.debug("[SkyBox] model=%s"%self.modelFile)
		self.node  = loader.loadModel(self.modelFile)
		
		#print("tf1 = %s, tf2 = %s"%(self.texture1File,self.texture2File))
		
		if self.texture1File != '' and self.texture2File == '':
			#LOG.debug("[SkyBox] single texture = %s"%self.texture1File)
			t = loader.loadTexture(self.texture1File)
			self.node.setTexture(t)
			
		elif self.texture1File != '' and self.texture2File != '':
			#LOG.debug("[SkyBox] texture staging 1 = %s, 2 = %s"%(self.texture1File,self.texture2File))
			t1 = loader.loadTexture(self.texture1File)
			t1.setWrapU(Texture.WMClamp)
			t1.setWrapV(Texture.WMClamp)
			ts1 = TextureStage('Space')
			ts1.setSort(self.texture1Sort)
			
			t2 = loader.loadTexture(self.texture2File)
			t2.setWrapU(Texture.WMClamp)
			t2.setWrapV(Texture.WMClamp)
			ts2 = TextureStage('SpaceClouds')
			ts2.setSort(self.texture2Sort)
			self.node.setTexture(ts1, t1)
			self.node.setTexture(ts2, t2)
		if self.shaderFile:
			LOG.debug("[SkyBox] shader = %s"%self.shaderFile)
			skyShader = Shader.load("./data/shaders/%s"%self.shaderFile)
			self.node.setShader(skyShader)
		
		# Should this be scaled here or done to the model?
		# It doesn't look like scaling the objects looks any different.
		self.node.setScale(280)
		
		# make sure it's drawn first (this can be done with shaders?)
		self.node.setBin('background', 0)
		
		# dont set depth attribute when rendering the sky (this can be done with shaders?)
		self.node.setAttrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
		
		# We don't want shadows on the skybox
		self.node.setLightOff()
		
		# Render
		self.node.reparentTo(self.parent)
		taskMgr.add(self.moveSkyTask, "Move the sky box with the cam")
		
		#LOG.debug("[SkyBox] done rendering")
		
	def moveSkyTask(self, Task):
		camPos=camera.getPos(render)
		#make sure the skybox doesn't move if we jump
		#camPos.setZ(0)
		self.node.setPos(camPos)
		return Task.cont
