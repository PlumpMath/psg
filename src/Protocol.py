''' Protocol.py
	Author:			Chad Rempp
	Date:			2009/05/30
	Purpose:		This module defines the network communication protocol.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			None
	'''

# System messages
MSG_NONE            = 0  # No message
MSG_PING_REQ        = 1  # No data passed
MSG_PING_RES        = 2  # No data passed
MSG_DISCONNECT_REQ  = 3  # No data passed
MSG_DISCONNECT_RES  = 4  # No data passed
# Pre-game server messages
MSG_AUTH_REQ        = 10 # username (String), password (String)
MSG_AUTH_RES        = 11 # 0=Failed, 1=Already connected, 2=Invalid password, 3=Ok
MSG_MAPLIST_REQ     = 12 # No data passed
MSG_MAPLIST_RES     = 13 # mapname (String), mapfilename (String), md5sum (String)
MSG_GAMELIST_REQ    = 14 # No data passed
MSG_GAMELIST_RES    = 15 # id (uint32), name (String), maxplayers(uint32), mapname (String), starttime (uint32), turnnum (uint32)
MSG_NEWGAME_REQ     = 16 # gameName (String), mapfile (String), maxplayers (uint32)
MSG_NEWGAME_RES     = 17 # 0=Failed, otherwise returns gameid
MSG_JOINGAME_REQ    = 18 # id (uint32)
MSG_JOINGAME_RES    = 19 # 0=No such game, 1=Game full, 2=Ok
# In-game server messages
MSG_CHAT_SEND       = 30 #
MSG_CHAT_RECV       = 31 #
MSG_UNITMOVE_SEND   = 32 #
MSG_UNITMOVE_RECV   = 33 #
MSG_UNITATTACK_SEND = 34 #
MSG_UNITATTACK_RECV = 35 #
MSG_UNITINFO_SEND   = 36 #
MSG_UNITINFO_RECV   = 37 #
MSG_ENDTURN_SEND    = 38 #
MSG_ENDTURN_RECV    = 39 #
