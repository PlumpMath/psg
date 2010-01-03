''' View.py
	
	Game views are the different views of the game.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			
'''

# Panda imports
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import AmbientLight
from pandac.PandaModules import DirectionalLight
from pandac.PandaModules import Vec4

# PSG imports
import Event
from Settings import GameSettings
from GXEng import SkyBox
from GXEng import CameraMgr

class GameView(object):
	'''The main view class for graphics'''
	def __init__(self):
		print("Creating GameView")
		base.disableMouse()
		#res = GameSettings().getSetting('RESOLUTION').split()[0].split('x')
		#self.xRes = int(res[0])
		#self.yRes = int(res[1])
		
		self.sky = SkyBox.SkyBox(render)
		self.camera = CameraMgr.CameraManager()
		
	def light(self):
		aLight = AmbientLight('aLight')
		dLight = DirectionalLight('dLight')
		aLight.setColor( Vec4(.6, .7, .8, 1) )
		dLight.setColor( Vec4( 0.9, 0.8, 0.9, 1 ) )
		alNP = render.attachNewNode(aLight) 
		dlNP = render.attachNewNode(dLight)
		dlNP.setHpr(0, -45, 0)
