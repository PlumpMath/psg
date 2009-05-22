from __future__ import division
''' Gui.py
	Author:			Chad Rempp
	Date:			2009/05/07
	Purpose:		The core GUI classes.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			
	'''
VERSION = 0.1
import sys, time
from direct.gui.DirectGui import *
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import TextNode
from pandac.PandaModules import TransparencyAttrib
from Util import frange
import Event
''' Variable naming convention
    _f_xxxx  Frame
    _l_xxxx  Label
    _b_xxxx  Button
    _g_xxxx  Geom
'''


# GUI Constants
GAMEWINDOW   = (0.3961,0.3961,0.3961,0.6)
CONTAINERBAR = (0.07,0.094,0.1255,0.9)
CONTAINER    = (0.3961,0.3961,0.3961,0.6)

winProps = WindowProperties( base.win.getProperties() )
x_res = winProps.getXSize()
y_res = winProps.getYSize()
ratio = x_res/y_res
print(base.getAspectRatio())

def tpc(coord,y=False): # To Panda Coordinate
    '''BUG! - Y values below 0 in panda coords are not converting correctly'''
    ratio   = x_res/y_res # Ratio for aspect2d
    shifter = x_res/2
    if y:
        scaler = -1/shifter
    else:
        scaler = ratio/shifter
    return ((coord - shifter) * scaler)

class Container(DirectFrame):
    def __init__(self, parent, pos=(0,0), height=160, width=190):
        self.parent = parent
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.height = height
        self.width  = width
        self.bar_height = 20
        self.frameSize = (tpc(self.x_pos),
                          tpc(self.x_pos+self.width),
                          tpc(self.y_pos+self.height,True),
                          tpc(self.y_pos,True))
        self.containerSize = (tpc(self.x_pos),
                          tpc(self.x_pos+self.width),
                          tpc(self.y_pos+self.height,True),
                          tpc(self.y_pos+self.bar_height,True))
        self.barSize= (tpc(self.x_pos),
                          tpc(self.x_pos+self.width),
                          tpc(self.y_pos+self.bar_height,True),
                          tpc(self.y_pos,True))
        self.color = CONTAINER
        self.x_scale = 0.23
        self.y_scale = 0.2
        self._g_container = loader.loadModel('psg_theme.egg').find('**/container')
        self._g_bar =  loader.loadModel('psg_theme.egg').find('**/container_bar')
        DirectFrame.__init__(self, self.parent, frameSize=self.frameSize, frameColor=self.color)
        self._f_container = DirectFrame(aspect2d,
               frameColor=(0,0,0,0),
               frameSize=self.containerSize,
               geom=self._g_container,
               geom_scale=(self.x_scale,self.y_scale,0),
               geom_pos=(tpc(self.x_pos+(self.width/2)),
                         0,
                         tpc(self.y_pos+(self.height/2),True)))
        self._l_bar=DirectLabel(aspect2d,
              frameColor=(0,0,0,0),
              frameSize=self.barSize,
              geom=self._g_bar,
              geom_scale=(0.13,0.155,0),
              geom_pos=(tpc(self.x_pos+(self.width/2)),
                          0,
                          tpc(self.y_pos+(self.bar_height/2),True)),
              text='',
              text_scale=0.048,
              text_fg=(1,1,1,1),
              text_pos=(tpc(self.x_pos+(self.width/2)),
                          tpc(self.y_pos+(self.bar_height/2)+6,True)))
        
    def slide_in(self):
        interval = frange(0,0.2,0.01)
        interval.reverse()
        print(interval)
        for y in interval:
            self.geom.setScale(y)
            self._f_container.setGeom=self.geom
            time.sleep(0.1)
    
    def slide_out(self):
        pass
    

class EntityContainer(Container):
    def __init__(self, parent, pos=(0,0), height=160, width=190):
        Container.__init__(self, parent, pos, height, width)
        self.pos_classlabel=(tpc(self.x_pos+(50/2)-10),
                     tpc(self.y_pos+20+20,True))
        self.pos_classvalue=(tpc(self.x_pos+(50/2)+45),
                     tpc(self.y_pos+20+20,True))
        
        self.pos_movelabel=(tpc(self.x_pos+(50/2)),
                     tpc(self.y_pos+20+40,True))
        self.pos_movevalue=(tpc(self.x_pos+(50/2)+45),
                     tpc(self.y_pos+20+40,True))
        
        self.pos_sensorlabel=(tpc(self.x_pos+(50/2)-7),
                     tpc(self.y_pos+20+60,True))
        self.pos_sensorvalue=(tpc(self.x_pos+(50/2)+45),
                     tpc(self.y_pos+20+60,True))
        
        self.pos_attacklabel=(tpc(self.x_pos+(50/2)-8),
                     tpc(self.y_pos+20+80,True))
        self.pos_attackvalue=(tpc(self.x_pos+(50/2)+45),
                     tpc(self.y_pos+20+80,True))
        
        DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='Class',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_classlabel)
        DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='Movement',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_movelabel)
        DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='Sensor',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_sensorlabel)
        DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='Attack',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_attacklabel)
        
        self._l_classvalue = DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_classvalue)
        self._l_movevalue = DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_movevalue)
        self._l_sensorvalue = DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_sensorvalue)
        self._l_attackvalue = DirectLabel(self._f_container,
               frameColor=(0,0,0,0),
               text='',
               text_scale=0.040,
               text_fg=(0,1,1,1),
               text_pos=self.pos_attackvalue)
        
    def setValues(self, entity):
        print("ENTITY = " + str(entity))
        self._l_bar['text']=entity.owner
        self._l_classvalue['text'] = entity.type
        self._l_movevalue['text'] = str(entity.moveRad)
        self._l_sensorvalue['text'] = str(entity.sensorRad)
        self._l_attackvalue['text'] = str(entity.attackRad)

class GameWindow(DirectFrame):
    def __init__(self):
        #print('Setting up GUI')
        self.parent = aspect2d
        self.size = (tpc(x_res-200),tpc(x_res),-1,1)
        self.color = GAMEWINDOW
        # BUG: This is invisible
        DirectFrame.__init__(self, self.parent,
                             frameSize=self.size,
                             frameColor=self.color)
        # This fixes the bug
        self._f_background = DirectFrame(self,
                             frameSize=self.size,
                             frameColor=self.color)
        
        self.objectContainer = EntityContainer(self,pos=(x_res-195,15))
        self._b_menu = DirectButton(self,
                             #frameSize=(tpc(x_res-190),tpc(x_res-150),tpc(y_res-10),tpc(y_res-30)),
                             scale=0.05,
                             pos=(tpc(x_res-170),0,-0.95),
                             text="Menu",
                             command=self.showMenu)
        self._b_endturn = DirectButton(self,
                             #frameSize=(tpc(x_res-190),tpc(x_res-150),tpc(y_res-10),tpc(y_res-30)),
                             scale=0.05,
                             pos=(tpc(x_res-70),0,-0.95),
                             text="End Turn",
                             command=self.endTurn)
        Event.Dispatcher().register(self, 'E_UpdateGUI', self.updateGUI)
        
    def showMenu(self):
        print("SHOW MENU")
        #Event.Dispatcher().broadcast(Event.Event('E_ShowMenu', src=self, data=selection))
        
    def endTurn(self):
        print("END TURN")
        Event.Dispatcher().broadcast(Event.Event('E_EndTurnt', src=self))
        
    def updateGUI(self, evt):
        print("UPDATE GUI" + str(evt.data))
        self.objectContainer.setValues(evt.data)
        
