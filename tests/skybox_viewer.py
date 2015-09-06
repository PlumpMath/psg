from panda3d.core import loadPrcFileData 
loadPrcFileData("", 'basic-shaders-only 0')
#loadPrcFileData("", "want-pstats 1")
#loadPrcFileData("", "want-directtools 1")
#loadPrcFileData("", "want-tk 1")
#loadPrcFileData("", "win-size 1280 1024")
loadPrcFileData("", "win-size 1024 768")

import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject

from direct.interval.IntervalGlobal import * 
from pandac.PandaModules import * 
from direct.filter.CommonFilters import CommonFilters
from direct.task import Task

import sys, os, math

DEBUG=4

os.chdir('../')

class World(DirectObject):
	def __init__(self):
		#sys.path.append('../game/GXEng')
		sys.path.append('./')
		from game.Util.Log import LogConsole
		import __builtin__
		__builtin__.LOG = LogConsole()
		from game.GXEng import SkyBox
		from game.GXEng import GXO
		from game.GXEng import GXMgr
		
		#base.camLens.setFov(60)
		#camera.setPos(-50,-50,0)
		#camera.lookAt(0,0,0)
		
		base.cam.node().setCameraMask(GXMgr.MASK_GXM_VISIBLE)
		
		self.accept('esc', sys.exit)
		
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
		
		base.bufferViewer.enable( 1 )
		star = GXO.GXOStar()
		
		sb.render()
		
	def lightTest01(self):
		''' Create an ambient light '''
		alight = AmbientLight('ambient01') 
		alight.setColor(VBase4(0.3, 0.3, 0.3, 1)) 
		alnp = render.attachNewNode(alight) 
		render.setLight(alnp)
		
	def lightTest02(self):
		''' Create a point light '''
		plight = PointLight('point02') 
		plight.setColor(VBase4(0.8, 0.8, 0.8, 1)) 
		plnp = render.attachNewNode(plight) 
		plnp.setPos(0, 0, 1) 
		
		render.setLight(alnp)
		
	def lightTest03(self):
		''' Create a point light attached to a model '''
		s = loader.loadModel("../data/models/sun_01.egg")
		s.setPos(0,70,1)
		s.reparentTo(sbNode)
		plight = PointLight("point02") 
		plight.setColor(VBase4(.9,.9,.9,1)) 
		plight.setAttenuation(Point3(.1,0,.01)) 
		plnp = render.attachNewNode(plight)
		plnp.setPos(0,70,1)
		render.setLight(plnp)
		
	
	def volumetricLightTest(self, model):
		fltr = CommonFilters(base.win, base.cam) 
		fltr.setVolumetricLighting(model,64,2,.85,0.3)
		#self,
		#caster,
		#numsamples = 32,
		#density = 5.0,
		#decay = 0.1,
		#exposure = 0.1
		
	def bloomTest(self):
		fltr.setBloom(blend=(1,0,0,1),mintrigger=.6, maxtrigger=1, desat=-.5,intensity=3,size=1) 
		#def setBloom	(	 	self,
		#	blend = (0.3,0.4,
		#	mintrigger = 0.6,
		#	maxtrigger = 1.0,
		#	desat = 0.6,
		#	intensity = 1.0,
		#	size = "medium"	 
		#)

	
#from pandac.PandaModules import PStatClient
#PStatClient.connect()
#base.startDirect()

w = World()
run()
