''' Game.py
	Author:			Chad Rempp
	Date:			2009/05/25
	Purpose:		Holds the game object.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			
	'''
	
class ClientGame:
	''' The game class stores all information for active games.'''
	def __init__(self, id=0, name='New Game', maxplayers=2, map='', starttime=0, turnnumber=0):
		''' Creates a new game.
			id (Int): the unique id of this game
			name (String): the name of this game
			maxplayers (Int): maximum players allowed to participate
			map (String): the file name of the map being used'''
		self.id         = id
		self.name       = name
		self.players    = []
		self.maxPlayers = maxplayers
		self.map        = map
		self.mapFile    = map.replace(' ','')+'.map'
		self.startTime  = starttime
		self.turnNumber = turnnumber
