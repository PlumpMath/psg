''' GXMgr.py
	
	The graphics engine manager. This is the facade for the graphics system.

	Author:			Chad Rempp
	Date:			2009/12/14
	License:		GNU LGPL v3
	Todo:			
'''

# Panda imports
from pandac.PandaModules import FrameBufferProperties
from pandac.PandaModules import GraphicsPipe
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import AmbientLight
from pandac.PandaModules import DirectionalLight
from pandac.PandaModules import Vec4

# PSG imports
from Settings import GameSettings
from GXEng import Representation
from GXEng import SkyBox
from GXEng import CameraMgr


class GXMgr(object):
	''' Document me! '''
	
	views = []
	
	def __init__(self):
		LOG.notice("Starting GX Manager")
		
		# GXMgr no longer uses dispatcher for communication . I am worried that
		# a message will not arrive and game state will be out of sync with the
		# representations.
		
		# The following code should proabably be moved somewhere else
		showFPS = GameSettings().showFPS
		base.setFrameRateMeter(showFPS)
		
	
	def buildRepresentation(self, entity):
		''' Use the entity to build the appropriate representation. Return
			a reference to the representation instance when done.
		'''
		
		if (entity.__class__.__name__[:6] == 'Entity'):
			# Should wrap this in a try/except
			kls = "Representation%s"%entity.__class__.__name__[6:]
			LOG.notice("Building a %s"%kls)
			rClass = getattr(Representation, kls)
			
		return rClass()
		
	def loadMap(self, map):
		''' Load the grapics objects defined in the map.
			
			This isn't the way I want to do this. We should not make the GXEng
			dependent on the structure of the map.
		'''
		
		#For now we setup a dummy environment
		self.sky = SkyBox.SkyBox(render)
		self.camera = CameraMgr.CameraManager()
		
		aLight = AmbientLight('aLight')
		dLight = DirectionalLight('dLight')
		aLight.setColor( Vec4(.6, .7, .8, 1) )
		dLight.setColor( Vec4( 0.9, 0.8, 0.9, 1 ) )
		alNP = render.attachNewNode(aLight) 
		dlNP = render.attachNewNode(dLight)
		dlNP.setHpr(0, -45, 0)
		
		self.sky.render()
		
	def makeGameEngine(self):
		''' Creates a new game engine based on settings in GameSettings.
			Information for this came from here
			http://panda3d.org/phpbb2/viewtopic.php?t=2848'''
		
		LOG.notice("GXMgr - Making Game Engine")
		
		# Create a new FrameBufferProperties object using our settings
		fbProps = FrameBufferProperties()
		fbProps.addProperties(FrameBufferProperties.getDefault())
		fbProps.setMultisamples(GameSettings().antiAlias)
		fbProps.setAlphaBits(GameSettings().alphaBits)
		fbProps.setDepthBits(GameSettings().colorDepth)
		
		# Create a WindowProperties object
		winProps = WindowProperties( base.win.getProperties() )
		winProps.setFullscreen(GameSettings().fullscreen)
		winProps.setUndecorated(GameSettings().fullscreen)
		winProps.setSize(GameSettings().xRes,GameSettings().yRes)
		winProps.setTitle('PSG - Project Space Game: Alpha')

		# Create the engine
		base.graphicsEngine.makeOutput(base.pipe,  # GraphicsPipe
								'mainGameOutput',  # Name
								0,                 # Sort
								fbProps,           # FrameBufferProperties
								winProps,          # WindowProperties
								GraphicsPipe.BFRequireWindow, # Flags
								base.win.getGsg()) # GraphicsStateGaurdian
		base.openMainWindow(props=winProps, gsg=base.win.getGsg(), keepCamera=1)
		