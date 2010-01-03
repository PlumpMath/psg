''' ViewStateMgr.py
	
	Controls the game views.
	Maybe move this to GXMgr.py

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			
'''

# Panda imports
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import NodePath
from pandac.PandaModules import Point3
from pandac.PandaModules import TextureStage
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4

# PSG imports
import Event
from Settings import GameSettings
from GameConsts import *
from GSEng import Entity
from GXEng import Grid
from GXEng import View
from GXEng import GeomObjects
from GXEng import Representation


class ViewStateManager(object):
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

