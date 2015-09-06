''' Interface.py
	
	Abstract Interface class for interacting with the Game Server.
	
	Author:			Chad Rempp
	Date:			2009/12/31
	License:		GNU LGPL v3
	Todo:			
'''


class Interface(object):
	def __init__(self, server):
		self._server = server