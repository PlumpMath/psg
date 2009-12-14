from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import AmbientLight
from pandac.PandaModules import DirectionalLight
from pandac.PandaModules import Vec4
from Settings import GameSettings
import SkyBox
import CameraMgr
import Event

class GameView():
	"""The main view class for graphics"""
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
