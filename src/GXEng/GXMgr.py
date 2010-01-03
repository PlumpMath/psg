''' GXMgr.py
	
	The graphics engine manager. This is the facade for the graphics system.

	Author:			Chad Rempp
	Date:			2009/12/14
	License:		GNU LGPL v3
	Todo:			
'''

class GXMgr(object):
	'''
	'''
	def __init__(self):
		LOG.notice("Starting GX Manager")
		
		# Put this somewhere
		base.setFrameRateMeter(gcli.gst.showFPS)
	
	def makeGameEngine(self):
		''' Creates a new game engine based on settings in GameSettings.
			Information for this came from here
			http://panda3d.org/phpbb2/viewtopic.php?t=2848'''
		
		LOG.notice("  GXMgr - Making Game Engine")
		
		# Create a new FrameBufferProperties object using our settings
		fbProps = FrameBufferProperties()
		fbProps.addProperties(FrameBufferProperties.getDefault())
		fbProps.setMultisamples(gcli.gst.antiAlias)
		fbProps.setAlphaBits(gcli.gst.alphaBits)
		fbProps.setDepthBits(gcli.gst.colorDepth)
		
		# Create a WindowProperties object
		winProps = WindowProperties( base.win.getProperties() )
		winProps.setFullscreen(gcli.gst.fullscreen)
		winProps.setUndecorated(gcli.gst.fullscreen)
		winProps.setSize(gcli.gst.xRes,gcli.gst.yRes)
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
		