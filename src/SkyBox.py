from direct.task import Task 
from pandac.PandaModules import DepthWriteAttrib
from pandac.PandaModules import Fog
from pandac.PandaModules import TextureStage
from pandac.PandaModules import Vec4
import os

# SkyBox------------------------------------------------------------------------
class SkyBox:
	""""""
	def __init__(self, parent):
		print(os.getcwd())
		self.node  = loader.loadModel("./data/models/skyboxObj.egg")
		self.texture1 = loader.loadTexture("./data/textures/tex_space_01.png")
		self.texture2 = loader.loadTexture("./data/textures/tex_space_01_trans.png")
		self.node.setTexture(self.texture1, 1)
		
		ts = TextureStage('ts')
		ts.setMode(TextureStage.MBlend)
		ts.setColor(Vec4(0.6, 0.753, 1, 1))
		self.node.setTexture(ts, self.texture2)
		self.node.setScale(280)
		
		# make sure it's drawn first
		self.node.setBin('background', 0)
		
		# dont set depth attribute when rendering the sky
		self.node.setAttrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
		
		self.node.setLightOff()
		
		# Render
		self.node.reparentTo(parent)
		
		taskMgr.add(self.moveSkyTask, "Move the sky box with the cam") 
		
	def moveSkyTask(self, Task):
		camPos=camera.getPos(render)
		#make sure the skybox doesn't move if we jump
		#camPos.setZ(0)
		self.node.setPos(camPos)
		return Task.cont
