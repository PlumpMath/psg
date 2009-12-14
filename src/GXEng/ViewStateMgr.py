from direct.interval.IntervalGlobal import *
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import NodePath
from pandac.PandaModules import Point3
from pandac.PandaModules import TextureStage
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4
from Settings import GameSettings
from GameConsts import *
#import Gui.GameMenu as GameGui
import Entity
import Event
import Grid
import View
import GeomObjects
import Representation


class ViewStateManager:
	views = []
	def __init__(self):
		#Event.Dispatcher().register(self, 'E_New_EntityRep',  self.handleNewEntity)
		self.repmanager = Representation.RepresentationManager()
		#self.gamemenu = GameGui.GameMenuForm()
		
		#gui.add(self.gamemenu)
		#self.grid = Grid.Grid(render, BOARDRADIUS, GRIDINTERVAL)
		
	def addView(self,  view):
		print("adding view")
		self.views.append(view)
		
	def getView(self, viewType):
		for view in self.views:
			if isinstance(view, viewType):
				return view
		return None

