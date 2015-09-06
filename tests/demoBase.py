# Panda settings
from panda3d.core import loadPrcFileData 
loadPrcFileData("", 'basic-shaders-only 0')
#loadPrcFileData("", "want-pstats 1")
#loadPrcFileData("", "want-directtools 1")
#loadPrcFileData("", "want-tk 1")
#loadPrcFileData("", "win-size 1280 1024")
loadPrcFileData("", "win-size 1024 768")

# Python imports
import sys, os, subprocess, time, signal

# Move to the base PSG directory so loading files is consistent
os.chdir('../')
# Append the base PSG directory to the path so we can import correctly
sys.path.append('./')

# Panda imports
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import PStatClient
from pandac.PandaModules import TextNode

# PSG imports
from game.GXEng import GXMgr

# Setup logging
from game.Util.Log import LogConsole
import __builtin__
__builtin__.LOG = LogConsole()

DEBUG=4

class DemoBase(DirectObject):
	def __init__(self):
		
		base.cam.node().setCameraMask(GXMgr.MASK_GXM_VISIBLE)
		
		self.accept('escape', sys.exit)
		self.accept('h', self._helpToggle)
		self.accept('p', self._pstatsToggle)
		self.accept('g', self._sgraphToggle)
		self.accept('x', self._fullscrnToggle)
		self.accept('b', self._bufferToggle)
		self.accept('f', self._fpsToggle)
		
		#self.accept('q', self._pstatsServ)
		
		self._pstatProc = None
		self._sgraph    = False
		self._buffer    = False
		self._fps       = False
		self._help      = True
		
		self._helpOffText = "h: help"
		self._helpOnText  = "esc: exit\np: pstats\ng: scene graph\nx: fullscreen\nb: buffer view\nf: frame rate"
		self._helpTextObj = None
		self._helpToggle()
		
	def _helpToggle(self):
		textPos = (-1.3, 0.95)
		
		if self._helpTextObj: self._helpTextObj.destroy()
		
		if self._help:
			self._helpTextObj = OnscreenText(text=self._helpOffText, pos=textPos, scale=0.03, fg=(0.8, 0.8, 0.8, 1), align=TextNode.ALeft)
			self._help = False
		else:
			self._helpTextObj = OnscreenText(text=self._helpOnText, pos=textPos, scale=0.03, fg=(0.8, 0.8, 0.8, 1), align=TextNode.ALeft)
			self._help = True
			
	def _pstatsToggle(self):
		print("HI")
		if self._pstatProc:
			# TODO: Fix this. It does not terminate the pstats process.
			print("Terminating pstats pid=%s"%(self._pstatProc.pid))
			PStatClient.disconnect()
			self._pstatProc.terminate()
			time.sleep(2)
			#self._pstatProc.kill()
			#self._pstatProc.send_signal(signal.SIGTERM)
			#os.kill( self._pstatProc.pid , signal.SIGTERM)
		else:
			print("Starting pstats server")
			self._pstatProc = subprocess.Popen("pstats", shell=True)
			print("  pstats proc: pid=%s"%(self._pstatProc.pid))
			time.sleep(1)
			print("Connecting to pstats server")
			PStatClient.connect()
		
	def _sgraphToggle(self):
		if self._sgraph:
			# TODO: Fix this. It crashes
			print("Closing scene graph browser")
			#base.startDirect(0,0,0)
			#self._sgraph = False
		else:
			print("Starting scene graph browser")
			base.startDirect()
			self._sgraph = True
			
	def _fullscrnToggle(self):
		pass
		
	def _bufferToggle(self):
		if self._buffer:
			print("Closing buffer viewer")
			base.bufferViewer.enable(0)
			self._buffer = False
		else:
			print("Starting buffer viewer")
			base.bufferViewer.enable(1)
			self._buffer = True
			
	def _fpsToggle(self):
		if self._fps:
			print("Closing frame rate meter")
			base.setFrameRateMeter(False)
			self._fps = False
		else:
			print("Starting frame rate meter")
			base.setFrameRateMeter(True)
			self._fps = True
		
	def addKey(self, key, function, msg):
		self.accept(key, function)
		self._helpOnText += "\n%s: %s"%(key, function)
		if (self._help):
			self._helpToggle()
			self._helpToggle()
	
def rundemo():
	run()
	