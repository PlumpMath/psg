from pandac.PandaModules import loadPrcFile
loadPrcFile("cfg/client.config")
from pandac.PandaModules import * 
import direct.directbase.DirectStart
from gui.keys import Keys
from gui.core import GUI,To2D
from gui.psgtheme import PSGTheme
from gui.controls import *
from gui.widgets import *

class MainScreen:
	def __init__(self):
		self.loadBackground()
	
	def loadBackground(self):
		self.background = OnscreenImage(image = 'data/images/menubackground_pot.png',
		   pos = (0, 0, 0), scale= (1, 1, 1), parent=render2d)
		#self.title = OnscreenText(text = '',
		#	pos = (0, 0.7), scale = 0.27, fg=Vec4(0.9,0.9,1, 1), 
		#	align=TextNode.ACenter, parent=render2d, 
		#	 font=loader.loadFont('cmss12.egg'))

class MainForm(Form):
	''' The main game menu'''
	def __init__(self):
		Form.__init__(self,'Game Menu',pos=Vec2(250,200),size=Vec2(300,300))
		
		# Dont show close or sizer button and disable drag.
		self.x.node.hide()
		self.sizer.node.hide()
		self.things[0].onClick=lambda b,k,m : None
		
		self.add(Button('New Game',pos=Vec2(80,40), size=(150,30), point=20, onClick=self.handle));
		self.add(Button('Load Game',pos=Vec2(80,80), size=(150,30), point=20,onClick=self.handle));
		self.add(Button('Display Settings',pos=Vec2(80,120), size=(150,30), point=20,onClick=self.handle));
		self.add(Button('Audio Settings',pos=Vec2(80,160), size=(150,30), point=20,onClick=self.handle));
		self.add(Button('Credits',pos=Vec2(80,200), size=(150,30), point=20,onClick=self.handle));
		self.add(Button('Exit',pos=Vec2(80,240), size=(150,30), point=20,onClick=self.handle));
		
	def handle(self):
		print("BUTTON")
		
gui = GUI(Keys(),PSGTheme())
m = MainForm()
gui.add(m)

run()