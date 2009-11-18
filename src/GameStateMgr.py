''' GameStateMgr.py
	Author:			Chad Rempp
	Date:			2009/05/27
	Purpose:		
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			
'''

# Python imports
import sys, random, cPickle

# Panda imports
from pandac.PandaModules import CollisionHandlerQueue
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionRay
from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import GeomNode
from pandac.PandaModules import Plane
from pandac.PandaModules import Point3
from pandac.PandaModules import Vec3

# PSG imports
import Controller
import GeomObjects
import Event
import Entity
import Player
import Map
from Util import Singleton
from Game import ClientGame

# GameState---------------------------------------------------------------------
class GameStateManager:
	"""A class that keeps track of the game state."""
	__metaclass__=Singleton
	
	gameId     = 0
	gameName   = ''
	players    = []
	turnNumber = 0
	map        = None
	startTime  = 0
	
	# States
	s_WaitingForSelection = True
	s_MoveCursor   = False
	s_AttackCursor = False
	selected = None
	currentPlayer = None
	
	def __init__(self,  gameToLoad=None):
		self.entitymanager = Entity.EntityManager()
		Event.Dispatcher().register(self, 'E_Key_Move', self.onMoveKey)
		Event.Dispatcher().register(self, 'E_Key_Exit', self.onExitKey)
		Event.Dispatcher().register(self, 'E_EntitySelect', self.onEntitySelect)
		#Event.Dispatcher().register(self, 'E_EntityUnSelect', self.onEntityUnSelect)
		Event.Dispatcher().register(self, 'E_Mouse_1', self.onMouse1)
		self.selector = Controller.Selector()
		
	
	def onMoveKey(self, event):
		if isinstance(self.selected, ShipEntity):
				self.s_DoingMoveSelection  = True
				self.movehandler = MovementSelectionHandler(self, self.selected)
				self.game.mousecontroller.attach(self.movehandler)
	
	def onExitKey(self, event):
		# TODO - Handle this better.
		if self.s_MoveCursor:
			# Exit moving state
			self.selected.representation.unselectMove()
			self.selected = None
			self.s_MoveCursor = False
			self.s_WaitingForSelection = True
			self.selector.unpause()
		if self.s_AttackCursor:
			# Exit attacking state (do not execute)
			self.selected.representation.unselectAttack()
		else:
			Event.Dispatcher().broadcast(Event.Event('E_ExitProgram', src=self))
			
	def onMouse1(self, event):
		if self.s_MoveCursor:
			# Exit moving state (execute move)
			moveTo = self.selected.representation._movecursor.getPosition()
			self.selected.representation.unselectMove()
			self.selected.move(moveTo)
			# TODO - calc fuel usage
			self.selected.moved = True
			self.s_MoveCursor = False
			# Enter attacking state
			self.selector.unpause()
			self.selected.representation.selectAttack()
			self.s_AttackCursor = True
					
	def onEntitySelect(self, event):
		if self.s_WaitingForSelection:
			self.selected = self.entitymanager.getFromTag(event.data)
			if self.selected.moved is not True:
				# Enter moving state
				Event.Dispatcher().broadcast(Event.Event('E_UpdateGUI', src=self, data=self.selected))
				self.s_WaitingForSelection = False
				self.selected.representation.selectMove()
				self.s_MoveCursor = True
				self.selector.pause()
		if self.s_AttackCursor:
			if self.selected.attacked is not True:
				# Exit attacking state (execute attack)
				shipToAttack = self.entitymanager.getFromTag(event.data)
				self.selected.representation.fireRockets(shipToAttack.pos)
				self.selected.representation.unselectAttack()
				# TODO - damage calc
				self.selected.attacked = True
				self.s_AttackCursor = False
				self.selected = None
				# Enter waitingforselection state
				self.s_WaitingForSelection = True
			
	def newGame(self, game):
		''' Create game objects from the game object.
			game (ClientGame).'''
		print("NEWGAME-->")
		self.gameId     = game.id
		self.gameName   = game.name
		self.turnNumber = game.turnNumber
		self.mapFileName= game.mapFileName
		self.startTime  = game.startTime
		self.mapName    = game.mapName
		
		print(self.mapFileName)
		
		# Load map
		fh = open(Map.MAP_PATH+self.mapFileName,'rb')
		serializedMap = cPickle.load(fh)
		players = serializedMap.getPlayers()
		planets = serializedMap.getPlanets()
		ships   = serializedMap.getShips()
		#print('SM - %s'%str(serializedMap._planets))
		print("num planets = %d"%len(planets))
		print("num ships = %d"%len(ships))
		
		print(planets)
		# Players
		for p in players:
			self.players.append(Player(name=p['name'], faction=p['faction'], type=p['type'],ai=p['ai']))
			
		# Planets
		for e in planets:
			print(e)
			self.entitymanager.addEntity(e)
		
		# Ships
		for e in ships:
			print(e)
			self.entitymanager.addEntity(e)
			
		'''
		# Create players (for testing just 1 human, 1 computer)
		self.players.append(Player.Player("Player1"))
		self.players.append(Player.Player("Computer"))
		
		# Create planets
		for i in range(10):
			pos = Vec3(random.uniform(-200, 200), 
								random.uniform(-200, 200), 
								random.uniform(-30, 30))
			p = Entity.EntityPlanet(tag="Planet-"+str(i), pos=pos)
			self.entitymanager.addEntity(p)
			#p.addEntity(e)
		for i in range(3):
			pos = Vec3(i*20, 0, 0)
			e = Entity.EntityLightCapture(tag="Ship-"+self.players[0].name+"-"+str(i), pos=pos)
			e.owner = self.players[0].name
			self.entitymanager.addEntity(e)
		for i in range(3):
			pos = Vec3(i*20, 50, 0)
			e = Entity.EntityLightCapture(tag="Ship-"+self.players[1].name+"-"+str(i), pos=pos)
			e.owner = self.players[1].name
			self.entitymanager.addEntity(e)
		self.currentPlayer = self.players[0]
		'''
		
	def loadGame(self, gameToLoad):
		print("loadGame not implemented yet")
		
	def startGame(self):
		pass

class TurnMgr:
	_usedEntities = []
	def __init__(self):
		print("TurnMgr")
		
	def doTurnTask(self, Task, player):
		
		return Task.cont
		
	def endTurn(self):
		pass
