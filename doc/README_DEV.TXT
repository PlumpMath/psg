TODO

Main Menu
	* Design images for windows
	* New Game Menu
	* Load Game Menu
	* Settings Menu
		- Resolution (drop down)
			4:3___________
			640x480
			800x600
			1024x768
			1280x960
			1400x1050
			1600x1200
			5:4____________
			1280x1024
			8:5_____________
			1280x800
			1440x900
			1680x1050
			1920x1200
			16:9___________
			854x480
			1280x720
			1920x1080
		- Full Screen
		- FPS
		- Antialias (0,1,2,4,8,16)
		- Alpha bits (8, 16, 32)
		- Color depth (8, 16, 32)
		
Game Gui
	* Main form
		- Layout
		- Functionality
		- Buttons and their functions
		- Info and their sources
	* Extended forms	
	
Ship movement
	* Highlight effect (colors, trans, ...)
	* Line effect (colors, trans, ...)

NOTES ON INSTALLING TREEGUI
- copy treegui3/treegui/* to psg/src/GUI/Treegui
- copy treegui3/cfg/* to psg/cfg
- copy treegui3/rtheme/* to psg/src/GUI/rtheme
- for each file in psg/src/GUI/Treegui and psg/src/GUI/rtheme change the import statements. For example:
- change "from core import *" to "from GUI.Treegui.core import *"
- change "import eggatlas" to "from GUI.Treegui import eggatlas"
- in the file psg/src/GUI/rtheme/__init__.py change RAW_DIR = "rtheme" to RAW_DIR = "src/GUI/rtheme"
