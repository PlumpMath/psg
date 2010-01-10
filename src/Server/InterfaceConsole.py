''' InterfaceConsole.py
	
	Author:			Chad Rempp
	Date:			2009/12/31
	License:		GNU LGPL v3
	Todo:			
'''

# Python imports
import platform
import sys
import time

# PSG imports
from Server.Interface import Interface

OS_TYPE = platform.system()
if (OS_TYPE == 'Linux'):
	print("trying Linux")
	import select
elif (OS_TYPE == 'Windows'):
	print("trying win")
	import msvcrt
else:
	print('Operating system not supported, exiting')
	sys.exit()

class InterfaceConsole(Interface):
	# The following are for the console
	_haveCommand = True
	_command     = ''
	_commandTok  = []
	
	def __init__(self, server):
		super(InterfaceConsole, self).__init__(server)
		if (OS_TYPE == 'Linux'):
			taskMgr.add(self.__consoleTask_u, 'consoleTask', -38)
		elif (OS_TYPE == 'Windows'):
			taskMgr.add(self.__consoleTask_w, 'consoleTask', -38)
		
	def __consoleTask_u(self, Task):
		'''This task accepts commands for the server in a Unix environment.
		   We use select as a non-blocking input.'''
		if self._haveCommand:
			self.__handleCommand()
			#self._commandTok = self._command.split()
			#print(self._commandTok)
			print("psgconsole: "),
			sys.stdout.flush()
			self._command = []
			self._haveCommand = False
		r,w,x = select.select([sys.stdin.fileno()],[],[],0)
		if (len(r) != 0):
			cmd = sys.stdin.readline()
			self._command = cmd[0:len(self._command)-1]
			self._commandTok = cmd.split()
			self._haveCommand = True
		return Task.cont
	
	def __consoleTask_w(self, Task):
		'''This task accepts commands for the server in a Windows environment.
		   We use getch as a non-blocking input.'''
		if msvcrt.kbhit():
			c = msvcrt.getche()
			if (c == '\r'): self._haveCommand = True
			elif (c=='\b'):
				# TODO - Also clear the onscreen buffer of the character
				self._command = self._command[0:len(self._command)-1]
			else: self._command += c
		if self._haveCommand:
			cmd = self._command[0:len(self._command)-1]
			print(cmd)
			self._commandTok = cmd.split()
			print("\bpsg: " + self._command)
			self.__handleCommand()
			print("psg: "),
			self._command = []
			self._haveCommand = False
		return Task.cont
	
	def __handleCommand(self):
		''' Call the appropriate handler for the current console command.
		exit
		lsconn
		lsusers
		lsgames
		kill		-c# -u# -g#'''
		if (len(self._commandTok) > 0):
			if self._commandTok[0] == 'exit':
				self.__quit()
			elif self._commandTok[0] == 'lsconn':
				self.__lsConnections()
			elif self._commandTok[0] == 'lsusers':
				self.__lsUsers()
			elif self._commandTok[0] == 'lsgames':
				self.__lsGames()
			elif self._commandTok[0] == 'kill':
				self.__kill()
			else: # Unknown command
				self.__printLine('Unknown command, I understand these:')
				self.__printLine('lsconn      lsusers     lsgames')
				self.__printLine('kill')
		
	def __lsConnections(self):
		''' Print all current connections'''
		self.__printLine('\b_ADDR__________|_USER__________|_GAME__________')
		if (len(self._server.connections) == 0):
			self.__printLine("No connections")
		else:
			for c in self._server.connections:
				addr = c.getAddress().getIpString()
				user = 'NONE'
				for u in self._server.connectedUsers:
					if (u.connectedClient == c):
						user = u.username
				game = 'NONE'
				for g in self._server.games:
					if (c in g.connections):
						game = g.name
						break
				self.__printLine("%s|%s|%s"%(addr.ljust(15),user.ljust(15),game.ljust(15)))
				
	def __lsUsers(self):
		''' Print all users currently signed in'''
		self.__printLine('\b_USER__________|_ADDR__________|_GAME__________')
		if (len(self._server.registeredUsers) == 0):
			self.__printLine("No users")
		else:
			for u in self._server.registeredUsers:
				user = u.username
				game = ''
				addr = ''
				if u.connected:
					addr = u.connectedClient.getAddress().getIpString()
				self.__printLine("%s|%s|%s"%(user.ljust(15),addr.ljust(15),game.ljust(15)))
					
	def __lsGames(self):
		''' Print all active games.'''
		self.__printLine('\b_ID_|_NAME__________|_MAP___________|_MX_PL_|_CONN_|_TURN_|_RUNTIME_')
		if (len(self._server.games) == 0):
			self.__printLine("No games")
		else:
			for g in self._server.games:
				runtime = (int(time.time()) - g.startTime) # Divide by 60 for minutes
				self.__printLine("%s|%s|%s|%s|%s|%s|%s"%
								 (str(g.id).ljust(4),
								  g.name.ljust(15),
								  g.map.name.ljust(15),
								  str(g.numPlayers).ljust(7),
								  str(len(g.connections)).ljust(6),
								  str(g.turnNumber).ljust(6),
								  ("%0.1f"%g.runTime()).ljust(9)))
				
	def __kill(self):
		''' Depending on parameters kill a game, connection or user.'''
		
		if (len(self._commandTok) == 2):
			try:
				type = self._commandTok[1][1]
				id   = self._commandTok[1][3:]
				print('%s %s'%(type,id))
			except:
				self.__printLine('USAGE: kill -c=address -u=username -g=id')
			finally:
				if (type=='c'): # Kill client
					foundClient = False
					for c in self._server.connections:
						if (c.getAddress().getIpString() == id):
							foundClient = True
							self._server.disconnect(client)
					if not foundClient:
						self.__printLine('Did not find client %s'%id)
				elif (type=='u'): # Kill user
					foundUser = False
					for u in self._server.connectedUsers:
						if (u.username == id):
							foundUser = True
							self._server.disconnect(None, None, u.connectedClient)
					if not foundUser:
						self.__printLine('User %s not connected'%id)
				elif (type=='g'): # Kill game
					foundGame = False
					for g in self._server.games:
						if (g.id == id):
							for u in g.players:
								self._server.disconnect(None, None, u.connectedClient)
							self._server.games.remove(g)
				else:
					self.__printLine('USAGE: kill -c=address -u=username -g=id')
		else:
			self.__printLine('USAGE: kill -c=address -u=username -g=id')
		
	def __quit(self):
		''' Clean up and shutdown. Tell all connected clients that we are
			shutting down, close connections and quit.'''
		self._server.shutdown()
		
	def printNotice(self, msg):
		''' Print notices to stdout.
			TODO - add in log file option.'''
		print('NOTICE: %s'%msg)
		sys.stdout.flush()
	
	def __printLine(self, msg):
		''' This is the print function for the console commands.'''
		outMsg = msg
		if OS_TYPE == 'Linux':
			sys.stdout.flush()
			print(outMsg)
			sys.stdout.flush()
		elif OS_TYPE == 'Windows':
			print(outMsg)