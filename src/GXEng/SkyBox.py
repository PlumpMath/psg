''' SkyBox.py
	
	The sky box object
	
	Author:			Chad Rempp
	Date:			2009/12/12
	License:		GNU LGPL v3 
	Todo:			Serialize skybox, lights, camera
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
	
	def __init__(self, parent, modelFile='data/models/skybox_02.egg', shaderFile='data/shaders/sky.sha', textureFile1='data/textures/tex_skybox_01.jpg', textureFile2='data/textures/tex_skybox_cloud.png'):
		#print(os.getcwd())
		self.modelFile    = modelFile
		self.shaderFile   = shaderFile
		self.textureFile1 = textureFile1
		self.textureFile2 = textureFile2
		self.parent       = parent
		
		self.node  = loader.loadModel(self.modelFile)
		
		if self.textureFile1 != '' and self.textureFile2 == '':
			t = loader.loadTexture(self.textureFile)
			self.node.setTexture(t)
			
		elif self.textureFile1 != '' and self.textureFile2 != '':
			t1 = loader.loadTexture(self.textureFile1)
			t1.setWrapU(Texture.WMClamp)
			t1.setWrapV(Texture.WMClamp)
			ts1 = TextureStage('Space')
			ts1.setSort(1)
			
			t2 = loader.loadTexture(self.textureFile2)
			t2.setWrapU(Texture.WMClamp)
			t2.setWrapV(Texture.WMClamp)
			ts2 = TextureStage('SpaceClouds')
			ts2.setSort(2)
			
			
			self.node.setTexture(ts1, t1)
			self.node.setTexture(ts2, t2)
			
		if self.shaderFile:
			skyShader = Shader.load(self.shaderFile)
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
		
		
	def render(self):
		# Render
		self.node.reparentTo(self.parent)
		#taskMgr.add(self.moveSkyTask, "Move the sky box with the cam")
		
	def moveSkyTask(self, Task):
		camPos=camera.getPos(render)
		#make sure the skybox doesn't move if we jump
		#camPos.setZ(0)
		self.node.setPos(camPos)
		return Task.cont
