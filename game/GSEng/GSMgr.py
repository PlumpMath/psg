''' GameStateMgr.py
	
	
	
	Author:			Chad Rempp
	Date:			2009/05/27
	License:		GNU LGPL v3
	Todo:			
'''

# Python imports
import sys, random, cPickle

# PSG imports
from game import Controller
from game import Event
from game.GXEng import GXMgr
from game.GSEng import Entity
from game.GSEng import Player
from game.GSEng.Game import Game
from game.Util.Singleton import Singleton

class GSMgr(Game):
	'''A class that keeps track of the game state.'''
	
	__metaclass__ = Singleton
	
	_gxmgr  = None
	_entmgr = None
	_game   = None
	
	players = []
	
	# States
	s_WaitingForSelection = True
	s_MoveCursor   = False
	s_AttackCursor = False
	selected = None
	currentPlayer = None
	
	def __init__(self, clientconnection):
		'''
			TODO - Document
		'''
		LOG.debug("[GSMgr] Initializing")
		
		super(GSMgr, self).__init__()
		
		self._clientconnection = clientconnection
		
		self._entmgr = Entity.EntityManager()
		
		Event.Dispatcher().register(self, 'E_Key_Move', self.onMoveKey)
		Event.Dispatcher().register(self, 'E_Key_Exit', self.onExitKey)
		Event.Dispatcher().register(self, 'E_EntitySelect', self.onEntitySelect)
		#Event.Dispatcher().register(self, 'E_EntityUnSelect', self.onEntityUnSelect)
		Event.Dispatcher().register(self, 'E_Mouse_1', self.onMouse1)
		
		self.selector = Controller.Selector()
		
		
	def registerGXEng(self, gxmgr):
		'''
			TODO - Document
		'''
		
		LOG.debug("[GSMgr] registering GXMgr %s"%gxmgr)
		
		# The GSMgr needs to know about the GXMgr
		self._gxmgr = gxmgr
		
		# The EntityMagager needs to know about the GXMgr
		self._entmgr.registerGXEng(gxmgr)
	
	def onMoveKey(self, event):
		if isinstance(self.selected, Entity.EntityShip):
				self.s_DoingMoveSelection  = True
				self.movehandler = MovementSelectionHandler(self, self.selected)
				self.game.mousecontroller.attach(self.movehandler)
	
	def onExitKey(self, event):
		# TODO - Handle this better.
		if self.s_MoveCursor:
			# Exit moving state
			self.selected.rep.unselectMove()
			self.selected = None
			self.s_MoveCursor = False
			self.s_WaitingForSelection = True
			self.selector.unpause()
		if self.s_AttackCursor:
			# Exit attacking state (do not execute)
			self.selected.rep.unselectAttack()
		else:
			Event.Dispatcher().broadcast(Event.Event('E_ExitProgram', src=self))
			
	def onMouse1(self, event):
		if self.s_MoveCursor:
			# Exit moving state (execute move)
			moveTo = self.selected.rep._movecursor.getPosition()
			self.selected.rep.unselectMove()
			self.selected.move(moveTo)
			# TODO - calc fuel usage
			self.selected.moved = True
			self.s_MoveCursor = False
			# Enter attacking state
			self.selector.unpause()
			self.selected.rep.selectAttack()
			self.s_AttackCursor = True
					
	def onEntitySelect(self, event):
		LOG.debug("[GSMgr] Entity select")
		if self.s_WaitingForSelection:
			LOG.debug("[GSMgr] tag=%s"%event.data)
			self.selected = self._entmgr.getFromTag(event.data)
			LOG.debug("[GSMgr] Selected = %s"%self.selected)
			if self.selected.moved is not True:
				# Enter moving state
				LOG.debug("[GSMgr] State Transition <s_WaitingForSelection=>s_MoveCursor>")
				Event.Dispatcher().broadcast(Event.Event('E_UpdateGUI', src=self, data=self.selected))
				self.s_WaitingForSelection = False
				
				self.selected.rep.selectMove()
				
				self.s_MoveCursor = True
				self.selector.pause()
		if self.s_AttackCursor:
			if self.selected.attacked is not True:
				# Exit attacking state (execute attack)
				LOG.debug("[GSMgr] State Transition <s_AttackCursor=>s_WaitingForSelection>")
				shipToAttack = self._entmgr.getFromTag(event.data)
				self.selected.rep.fireRockets(shipToAttack.pos)
				self.selected.rep.unselectAttack()
				# TODO - damage calc
				self.selected.attacked = True
				self.s_AttackCursor = False
				self.selected = None
				# Enter waitingforselection state
				self.s_WaitingForSelection = True
	
	def loadState(self):
		pass
	
	def startGame(self, map):
		''' Create game objects and start game.'''
		
		LOG.debug("[GSMgr] Starting game with map %s"%map)
		
		def registerResp(status):
			''' dummy function. This should begin the turn mechanism.'''
			LOG.notice("Register response - %s"%status)
		
		# Set game parameters
		self.name = map.name
		self.numPlayers = map.numPlayers
		self.mapSize = map.mapSize
		
		# Load players
		self.players = map.playerList
		LOG.debug("[GSMgr]    Loaded %d players"%len(self.players))
		
		# Load entities
		entityCount = 0
		for e in map.entityList:
			self._entmgr.addEntity(e)
			entityCount += 1
		LOG.debug("[GSMgr]    Loaded %d entities"%entityCount)
		
		# Load lights
		lightCount = 0
		for l in map.lightList:
			self._gxmgr.addLight(l['type'], l['tag'], l['pos'], l['color'], l['hpr'])
			lightCount += 1
		LOG.debug("[GSMgr]    Loaded %d lights"%lightCount)
		
		# Load cameras
		cameraCount = 0
		for c in map.cameraList:
			self._gxmgr.addCamera(c)
			cameraCount += 1
		LOG.debug("[GSMgr]    Loaded %d cameras"%cameraCount)
		
		# Load skybox
		self._gxmgr.addSkybox(map.skybox)
		LOG.debug("[GSMgr]    Loaded skybox")
		
		# Turn on camera
		self._gxmgr.CameraMgr.startCamera()
		
		# We are done loading so register with the server
		#self._clientconnection.registerGame(self, registerResp)
		
class TurnMgr(object):
	_usedEntities = []
	def __init__(self):
		print("TurnMgr")
		
	def doTurnTask(self, Task, player):
		
		return Task.cont
		
	def endTurn(self):
		pass
