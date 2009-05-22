from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec4
import  GuiOld.MainMenu

class Menu:
	def __init__(self, base):
		self.base = base
		self.loadBackground()
		self.loadMain()
		
	def loadBackground(self):
		self.background = OnscreenImage(image = 'data/images/menubackground.png',
		   pos = (0, 0, 0), scale= (1, 1, 1), parent=render2d)
		self.title = OnscreenText(text = '',
			pos = (0, 0.7), scale = 0.27, fg=Vec4(0.9,0.9,1, 1), 
			align=TextNode.ACenter, parent=render2d, 
			 font=loader.loadFont('cmss12.egg'))
			
	def unloadBackground(self):
		self.background.destroy()
		self.title.destroy()
		
	def loadMain(self):
		self.menu = GuiOld.MainMenu.MainForm(self)
		gui.add(self.menu)
		
	def loadNew(self):
		self.menu = GuiOld.MainMenu.NewForm(self)
		gui.add(self.menu)
		
	def loadLoad(self):
		self.menu = GuiOld.MainMenu.LoadForm(self)
		gui.add(self.menu)

	def loadDisplay(self):
		self.menu = GuiOld.MainMenu.DisplayForm(self)
		gui.add(self.menu)

	def loadAudio(self):
		self.menu = GuiOld.MainMenu.AudioForm(self)
		gui.add(self.menu)
		
	def loadCredits(self):
		self.menu = GuiOld.MainMenu.CreditsForm(self)
		gui.add(self.menu)

	def showNew(self):
		self.menu.toggle()
		self.loadNew()
		
	def showLoad(self):
		self.menu.toggle()
		self.loadLoad()
		
	def showDisplay(self):
		self.menu.toggle()
		self.loadDisplay()
		
	def showAudio(self):
		self.menu.toggle()
		self.loadAudio()
		
	def showCredits(self):
		self.menu.toggle()
		self.loadCredits()
		
	def showMainFromNew(self):
		self.menu.toggle()
		self.loadMain()
		
	def showMainFromLoad(self):
		self.menu.toggle()
		self.loadMain()
		
	def showMainFromDisplay(self):
		self.menu.toggle()
		self.loadMain()
		
	def showMainFromAudio(self):
		self.menu.toggle()
		self.loadMain()
		
	def showMainFromCredits(self):
		self.menu.toggle()
		self.loadMain()
	
	def startGame(self):
		self.menu.toggle()
		self.unloadBackground()
		self.base.startGame()
	
	def exit(self):
		self.unloadBackground()
		self.base.exit()
