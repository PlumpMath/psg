import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
import sys

class World(DirectObject):
	def __init__(self):
		sys.path.append('../src')
		from GXEng.SkyBox import SkyBox
		base.camLens.setFov(60)
		camera.setPos(0,0,0)
		sb = SkyBox(render,
			    modelFile="../data/models/skybox_02.egg",
			    shaderFile="../data/shaders/sky.sha",
			    textureFile1="../data/textures/tex_skybox_01.jpg",
			    textureFile2="../data/textures/tex_skybox_cloud.png")
		
		sb.render()
		
w = World()
run()
