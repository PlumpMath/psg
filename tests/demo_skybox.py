# Demo Import
from demoBase import *

# Python imports

# Panda imports
from direct.interval.IntervalGlobal import * 
from pandac.PandaModules import * 
from direct.filter.CommonFilters import CommonFilters
from direct.task import Task

# PSG imports
from game.GXEng import SkyBox
from game.GXEng import GXO
from game.GXEng import GXMgr

class DemoSkybox(DemoBase):
	def __init__(self):
		DemoBase.__init__(self)
		
		sbNode = render.attachNewNode("Skybox")
		shipNode = render.attachNewNode("Ships")
		
		sb = SkyBox.SkyBox(sbNode,
			    modelFile="../data/models/skybox_03.egg")
			    #shaderFile="../data/shaders/sky.sha",
			    #texture1File="../data/textures/tex_skybox_01.jpg",
			    #texture2File="../data/textures/tex_skybox_cloud.png")
		
		# Load a model
		m = loader.loadModel("../data/models/ship_03.egg")
		m.reparentTo(shipNode)
		
		sb.render()
		

d = DemoSkybox()
rundemo()
