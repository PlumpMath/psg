''' Protocol.py

	This module defines the network communication protocol.
	
	On the server side the datagrams are opened by the __readTask. There the
	message ID is pulled out and the message is either handled by the server (if
	the ID is less than MSG_INGAME) or sent to the message router. The message
	router pulls out the next part of the datagram which is a game ID. The
	router then passes the message to the appropriate GameStateServer. At the
	GameStateServer the message is passed to the appropriate handler.
	
	DGS stands for DataGram Structure

	Author:			Chad Rempp
	Date:			2009/05/30
	License:		GNU LGPL v3 
	Todo:			
'''

#__________SYSTEM MESSAGES__________
MSG_NONE            = 0
#__________DGS__________
# Stub message to define a null message.
# This should never be sent.

MSG_PING_REQ        = 1
#__________DGS__________
# uint16  - message id

MSG_PING_RES        = 2
#__________DGS__________
# uint16  - message id

MSG_DISCONNECT_REQ  = 3
#__________DGS__________
# uint16  - message id

MSG_DISCONNECT_RES  = 4
#__________DGS__________
# uint16  - message id


#__________GAME-SETUP MESSAGES__________
MSG_AUTH_REQ        = 10
# uint16  - message id
# string  - username
# string  - password

MSG_AUTH_RES        = 11
#__________DGS__________
# uint16  - message id
# uint32  - response
#            0 = Failed
#            1 = Already authorized
#            2 = Invalid password
#            3 = Ok

MSG_MAPLIST_REQ     = 12
#__________DGS__________
# uint16  - message id

MSG_MAPLIST_RES     = 13
#__________DGS__________
# uint16  - message id
# string  - 'SOT' indicates the start of transmission
# string  - Map name
# string  - Map filename
# string  - Map MD5 ID
# string  - 'T' indicates the transmission will continue with another item
#         .
#         .
#         .
# string  - 'EOT' indicates the end of transmission

MSG_GAMELIST_REQ    = 14
#__________DGS__________
# uint16  - message id

MSG_GAMELIST_RES    = 15
#__________DGS__________
# uint16  - message id
# string  - 'SOT' indicates the start of transmission
# int32   - Game ID
# string  - Game name
# uint32  - Number of players
# string  - Map name
# uint32  - Start time
# uint32  - Turn number
# string  - 'T' indicates the transmission will continue with another item
#         .
#         .
#         .
# string  - 'EOT' indicates the end of transmission

MSG_NEWGAME_REQ     = 16
#__________DGS__________
# uint16  - message id
# string  - Game name
# string  - Map ID (MD5)
# uint32  - Number of players

MSG_NEWGAME_RES     = 17
#__________DGS__________
# uint16  - message id
# int32   - Status
#            -1 = Failure
#             0 = Need map
#            +X = X is an integer representing the game ID

MSG_JOINGAME_REQ    = 18
#__________DGS__________
# uint16  - message id

MSG_JOINGAME_RES    = 19
#__________DGS__________
# uint16  - message id
# uint32  - Status
#            0 = No such game
#            1 = Game full
#            2 = Ok
# string  - Map MD5 for the game

MSG_DOWNLOADMAP_REQ  = 20
#__________DGS__________
# uint16  - message id
# string  - Map ID (MD5)

MSG_DOWNLOADMAP_RES  = 21
#__________DGS__________
# uint16  - message id
# uint32  - Status
#            0 = No such map
#            1 = Success
#            2 = Failure
# string  - Map data string

MSG_DOWNLOADUPD_REQ  = 22
#__________DGS__________
# uint16  - message id
# string  - Version number

MSG_DOWNLOADUPD_RES  = 23
#__________DGS__________
# uint16  - message id
# uint32  - Status
#            0 = No such map
#            1 = Success
#            2 = Failure
# string  - Update data string

#__________IN-GAME MESSAGES__________
MSG_INGAME          = 50
#__________DGS__________
# Stub message to define the begining of in-game messages.
# This should never be sent.

MSG_CHAT_SEND       = 51
#__________DGS__________
# uint16  - message id

MSG_CHAT_RECV       = 52
#__________DGS__________
# uint16  - message id

MSG_UNITMOVE_SEND   = 53
#__________DGS__________
# uint16  - message id

MSG_UNITMOVE_RECV   = 54
#__________DGS__________
# uint16  - message id

MSG_UNITATTACK_SEND = 55
#__________DGS__________
# uint16  - message id

MSG_UNITATTACK_RECV = 56
#__________DGS__________
# uint16  - message id

MSG_UNITINFO_SEND   = 57
#__________DGS__________
# uint16  - message id

MSG_UNITINFO_RECV   = 58
#__________DGS__________
# uint16  - message id

MSG_ENDTURN_SEND    = 59
#__________DGS__________
# uint16  - message id

MSG_ENDTURN_RECV    = 60
#__________DGS__________
# uint16  - message id