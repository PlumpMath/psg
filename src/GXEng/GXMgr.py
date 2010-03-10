''' GXMgr.py
	
	The graphics engine manager. This is the facade for the graphics system.

	Author:			Chad Rempp
	Date:			2009/12/14
	License:		GNU LGPL v3
	Todo:			
'''

# Python imports
from new import classobj

# Panda imports
import pandac.PandaModules # for dynamic light creation
from pandac.PandaModules import FrameBufferProperties
from pandac.PandaModules import GraphicsPipe
from pandac.PandaModules import WindowProperties

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
	cameraMgr = None
	lightList = []
	
	def __init__(self):
		LOG.debug("[GXMgr] Initializing")
		
		# GXMgr no longer uses dispatcher for communication . I am worried that
		# a message will not arrive and game state will be out of sync with the
		# representations.
	
	def buildRepresentation(self, entity):
		''' Use the entity to build the appropriate representation. Return
			a reference to the representation instance when done.
		'''
		LOG.debug("[GXMgr] Building representation of entity %s"%entity)
		
		rClass = None
		if (entity.__class__.__name__[:6] == 'Entity'):
			# Should wrap this in a try/except
			kls = "Rep%s"%entity.__class__.__name__[6:]
			rClass = getattr(Representation, kls)
		
		LOG.debug("[GXMgr]   Built a %s"%kls)
		return rClass()
		
	
	def addLight(self, type, tag, pos, color, hpr):
		''' Create a light of the given type and assign the given properties.
			Dynamic class instantantiation is difficult due to the Panda module
			layout so we use conditionals
			TODO - support for attenuation.
		'''
		
		LOG.debug("[GXMgr] Adding light of type %s"%type)
		
		if hasattr(pandac.PandaModules, type):
			LOG.debug("[GXMgr] Found light class - %s"%type)
			
			if (type.lower() == 'ambientlight'):
				from pandac.PandaModules import AmbientLight
				l = AmbientLight(tag)
				if color:
					l.setColor(color)
				lnp = render.attachNewNode(l)
			elif (type.lower() == 'directionallight'):
				from pandac.PandaModules import DirectionalLight
				l = DirectionalLight(tag)
				if color:
					l.setColor(color)
				lnp = render.attachNewNode(l)
				if hpr:
					lnp.setHpr(hpr)
			elif (type.lower() == 'pointlight'):
				from pandac.PandaModules import PointLight
				l = PointLight(tag)
				if color:
					l.setColor(color)
				lnp = render.attachNewNode(l)
				if pos:
					lnp.setPos(pos)
			elif (type.lower() == 'spotlight'):
				from pandac.PandaModules import Spotlight
				l = Spotlight(tag)
				if lens:
					lightLens = PerspectiveLens()
					l.setLens(lightLens)
				if color:
					l.setColor(color)
				lnp = render.attachNewNode(l)
				if hpr:
					lnp.setHpr(hpr)
				if pos:
					lnp.setPos(pos)
			
			self.lightList.append(lnp)
			render.setLight(lnp)
		else:
			LOG.error("[GXMgr] Unknown light class - %s"%type)
		
	def addSkybox(self, skybox):
		''' Add a skybox. '''
		
		LOG.debug("[GXMgr] Adding skybox %s"%skybox)
		self.sky = skybox
		self.sky.render()
	
	def addCamera(self, camera):
		'''
			TODO - Document
		'''
		
		LOG.debug("[GXMgr] Adding camera %s"%camera)
		self.CameraMgr = camera
		
	def makeGameEngine(self):
		''' Creates a new game engine based on settings in GameSettings.
			Information for this came from here
			http://panda3d.org/phpbb2/viewtopic.php?t=2848'''
		
		LOG.debug("[GXMgr] Building game engine")
		
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
		# The following code should proabably be moved somewhere else
		showFPS = GameSettings().showFPS
		base.setFrameRateMeter(showFPS)