''' ServerPlayer.py
	
	The game server handles sharing games between connected	clients and passes
	messages.
	
	Author:			Chad Rempp
	Date:			2010/01/01
	License:		GNU LGPL v3
'''

# Python imports
import hashlib
from datetime import datetime

# PSG imports
from GSEng.Player import Player

class ServerPlayer(Player):
	''' Stores all relevant information for a user.
		TODO - Implement connection history
	'''
	username         = ''
	password         = ''
	connected        = False
	connectedAddress = None
	connectedTime    = None
	connectHistory   = []
	connectedClient  = None
	connectedAddress = ''
	
	def __init__(self, usr, passwd):
		''' Creates a new user.
			usr (String): the user name
			passwd (String): the plain text password which is then encrypted
				and stored.'''
		super(ServerPlayer, self).__init__()
		self.username = usr
		h = hashlib.sha256()
		h.update(passwd)
		self.password = h.hexdigest()
		
	def authorize(self, passwd, client):
		''' Compares encrypted passwords to determine authorization, if
		    authorized we set the connection state for this user.
		    passwd (String): an encrypted password
		    client (Client): the client the user is connecting from.'''
		if (passwd == self.password):
			self.connect(client)
	
	def connect(self, client):
		''' Set up the users connection state.
			client (Client): the client the user is connecting from,'''
		self.connected = True
		self.connectedTime = datetime.now()
		self.connectedClient = client
		self.connectedAddress = client.getAddress().getIpString()
		self.connectHistory.append({client:self.connectedTime})
	
	def disconnect(self):
		''' Reset the users connection state.'''
		self.connected = False
		self.connectedTime = None