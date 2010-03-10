''' GameConsts.py
	
	Game settings that should not be visible via the GameSettings.

	Author:			Chad Rempp
	Date:			2009/12/04
	License:		GNU LGPL v3 
	Todo:			
'''

# Panda imports
from pandac.PandaModules import Vec4

SKYBOX_RADIUS = 100

MAX_GAME_PLAYERS = 10

# These can be set for debugging but should be blank for releases
DEFAULT_USERNAME = "chad"
DEFAULT_PASSWORD = "password1"

# Game board settings
BOARDRADIUS   = 50
GRIDINTERVAL  = 3
LINETHICKNESS = 1
GRIDCOLOR     = (0, 1, 0, 0)

MAP_PATH      = 'maps/'
MAP_EXT       = '.map'

EVENTS = ['E_All',
		  'E_Mouse_1', 
		  'E_Mouse_1_Up', 
		  'E_Mouse_2', 
		  'E_Mouse_2_Up', 
		  'E_Mouse_3', 
		  'E_Mouse_3_Up', 
		  'E_MouseWheel_Up', 
		  'E_MouseWheel_Down', 
		  'E_Key_CameraUp',
		  'E_Key_CameraUp-up',
		  'E_Key_CameraDown',
		  'E_Key_CameraDown-up',
		  'E_Key_CameraLeft',
		  'E_Key_CameraLeft-up',
		  'E_Key_CameraRight',
		  'E_Key_CameraRight-up',
		  'E_Key_ZUp',
		  'E_Key_ZDown',
		  'E_Key_ZUp-up',
		  'E_Key_ZDown-up',
		  'E_Key_Move',
		  'E_Key_Exit',
		  'E_New_Entity',
		  'E_New_EntityRep',
		  'E_EntitySelect',
		  'E_EntityUnSelect',
		  'E_UpdateGUI',
		  'E_StartGame',
		  'E_EndTurn',
		  'E_ExitGame',
		  'E_ExitProgram']