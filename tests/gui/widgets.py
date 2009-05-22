"""
    This containts the widgits the the tree gui system
    the widgits cannot contain other other widgits and are 
    the basic building blocks
"""
from pandac.PandaModules import *
from core import GUI,Clipper

def curry(func, *args, **kwds):
    def callit(*moreargs, **morekwds):
        kw = kwds.copy()
        kw.update(morekwds)
        return func(*(moreargs+args), **kw)
    return callit

class Widget(object):   
    """
        Base widgest for all widgets
    """
    skinType = None
      
    def __init__(self,pos=Vec2(0,0),size=Vec2(0,0)):
        """ you probably do not want to create a plain widgits
            but use of its derivitives """
        self.pos = pos
        self.size = Vec2(size)
        self.node = NodePath(self.__class__.__name__)   
        self.node.setPos(pos[0],0,pos[1])
        self.geom = None
        self.regenerate = True
        
    def setSize(self,size):
        """ sets the size """
        self.size = size
        self.regenerate = True
        gui.redraw()
        
    def getSize(self):
        """ gets the size of the object """
        return self.size
        
    def setPos(self,pos):
        """ sets the positoins of the gui object """
        self.pos = pos
        self.node.setPos(pos[0],0,pos[1])
        
    def onDrag(self,button,key,mouse):
        """ this function will start to drug the window """
        gui.drag = self   
        gui.dragPos = self.pos-gui.mouse
        self.parent.toFront(self)
                
    def getPos(self):
        """
            returns the positions of the widgit relative to
            its parent
        """
        return self.pos
    
    def resize(self):
        """ 
            resizes the gui object (many objects cant be 
            resized so in this case the functions does
            nothing 
        """
    
    def draw(self,pos,size):
        """ modifys the geometry of the object """
        if self.regenerate:
            self.regenerate = False
            if self.geom:
                self.geom.removeNode()
            if self.skinType:
                box = (self.skinType, Vec2(0,0),self.size,self)
                self.geom = gui.theme.generate(box)
                if self.geom:
                    self.geom.reparentTo(self.node)
        gui.theme.fixZ(self)
        
    def __str__(self):
        """ returns the string representaion of the object """
        v1,v2 = "",""
        try: v1 = str(self.value)
        except:pass
        try: v2 = str(self.getText())
        except:pass
        return "<%s %s %s>"%( self.__class__.__name__, v2, v1 )
              
    def reparentTo(self,node):
        """ attaches the gui object to a different node """
        self.node.reparentTo(node)
        
    def mouseEvent(self,key,mouse):
        """ Override this for your mouse event """
    
    def __getattr__(self, name):
        """ the gui object inherits many attributes of under laying node path """
        try:
            return object.__getattr__(name)
        except:
            try:
                return curry(self.node.DtoolClassDict[name],self.node)
            except:
                raise AttributeError(repr(self)+" does not have attribute "+name)

    def getNode(self):
        """ returs the under laying node of the object """
        return self.node
        
    def update(self):
        """ hart beat in order to see if the widgit needs updating """
             
class Lable(Widget):
    
    """ use this for short pice of static text """
    
    def __init__(self,textstring,pos=Vec2(0,0),point=14):
        """ create a gui lable """
        Widget.__init__(self,pos)
        self.text = TextNode("text")            
        self.text.setCardDecal(True)
        self.currentString = textstring
        self.text.setText(textstring)
        self.text.setTextColor(*gui.theme.LABLECOLOR)
        self.textNode = self.node.attachNewNode(self.text)     
        self.textNode.setScale(Vec3(point,1,-point)) 
        self.textNode.setPos(0,0,point) 
        
    def setText(self,textstring):
        """ sets the text of the object """
        textstring = str(textstring)
        if self.currentString != textstring:
            self.currentString = textstring
            self.text.setText(textstring)
        
    def getText(self):
        """ gest the text """
        return self.text.getText()
        
class Text(Lable):
    
    """ use this for long pice of dynamic text """
    
    def __init__(self,textstring,pos=Vec2(0,0),wrap=5,point=14):
        """ create a gui lable """
        Lable.__init__(self,textstring,pos,point=point)
        self.text.setWordwrap(wrap)
        
         
class BaseInput(Lable):
    
    """ this is the most primtive input widget """
    
    skinType = "INPUT"
    
    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,20),point=14):
        """ create a gui input """
        Lable.__init__(self,pos,size)
          
    def mouseEvent(self,key,mouse):
        """ mouse events are usd to focus the Base Input """
        gui.keys.focus = self
        return True
        
    def onKey(self,key):
        """ figure out what to do with the key after you get it """        
        text = self.text.getText()
        
        if key == "backspace":                
                self.text.setText( text[0:-1] )
        elif key == "enter":  
            self.onEnter(self)        
        elif key == "space":  
            self.text.setText( text + ' ' )
        else:
            self.text.setText( text + key )
        return True
        
    def onEnter(self,key):
        """ overide this """
     

class Input(BaseInput):
    
    """ much better input widget """
    
    skinType = "INPUT"
    
    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,20),point=14):
        """ create a gui input """
        from direct.gui.DirectGui import DirectEntry
        Widget.__init__(self,pos,size)
        self.textNode = DirectEntry(
                text = "" ,
                image=None, 
                frameSize=(0,100,0,.5),frameColor=(0,0,0,0) , geom = None,
                rolloverSound="",clickSound="",scale=(point,1,-point),
                width = size[0]*.07,
                command=self._onEnter,focusInCommand=self.onFocus,
                focusOutCommand=self.onUnFocus,initialText=textstring,
                 numLines = 1 ,focus=False)
        #self.textNode.setScale(1,1,-1) 
        self.textNode.setPos(0,0,point)
        self.textNode.reparentTo(self.node)
              
    def mouseEvent(self,key,mouse):
        """ handes mouse events """
        gui.keys.focus = self
        self.textNode['focus'] = True
        return True
     
    def onFocus(self):
        """ when the input gains focus """
        gui.keys.focus = self
        
    def onUnFocus(self):
        """ when the input looses focus """
        gui.keys.focus = None 
        
    def onKey(self,key):
        """ when it gets a key """
        return True
    
    def draw(self,*arg):
        """ updates the input object """
        if gui.keys.focus != self:
            self.textNode['focus'] = False
        if self.regenerate:
            self.textNode['text_fg'] = Vec4(*gui.theme.LABLECOLOR)
        self.textNode.reparentTo(self.node)
        BaseInput.draw(self,*arg)  

    def _onEnter(self,txt):
        """ low level on enter event"""
        self.onEnter(self)
    
    def setText(self,textstring):
        """ sets the text of the input """
        self.textNode.enterText(str(textstring))
        
    def getText(self):
        """ get the text of the input """
        return self.textNode.get()
    
    def mouseEvent(self,key,mouse):
        """ when the users does some thing with a mouse """
        gui.keys.focus = self
        self.textNode['focus'] = True
        return True
            
        
class Button(Lable):
    
    """ standard button """
    
    skinType = "BUTTON"
    
    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,16),point=14,onClick=None):
        """ create a gui input """
        Lable.__init__(self,textstring,pos,point)
        self.size = size
        if onClick: 
            self.onClick = onClick

    def mouseEvent(self,key,mouse):
        """ do what button does best """
        self.onClick(self,key,mouse)
        return True
    
    def onClick(self,button,key,mouse):
        """ overdie this """
        self.regenerate = True
        
class ProgressBar(Lable):
    
    skinType = "PROGRESS_BAR"
    
    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(100,16),point=14,onClick=None):
        """ create a gui input """
        Lable.__init__(self,textstring,pos,point)
        self.value = 0
        self.maxSize = size
        self.size = Vec2(0,size.getY())
        self.size.setX(size.getX()*self.value)
        
    def setValue(self,value):
        """ sets the value of the progress bar """
        self.value = value
        self.size.setX(self.maxSize.getX()*self.value)
        self.regenerate = True
        gui.redraw()        

class Radio(Button):
    """ 
        radio button ... only one button of this 
        type can be selected in a given parent 
    """
    skinType = "RADIOOFF"
    value = False
    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(20,20),point=14,onClick=None):
        """ creates a radio button (all radio buttons attached to the parent 
            will switch when one is clicked on """
        Button.__init__(self,"    "+textstring,pos,size,point,onClick)
            
    def onClick(self,button,key,mouse):
        """ 
            changes the state of the radio and 
            changaes the state of the radio buttons 
            around it
        """
        self.regenerate = True
        for thing in self.parent.things:
            if thing.__class__ == self.__class__:
                thing.value = False
                thing.regenerate = True
                thing.skinType = "RADIOOFF"
        self.value = not self.value
        if self.value:
            self.skinType = "RADIOON"
        else:
            self.skinType = "RADIOOFF"  


class Check(Button):
    """
        Standard on/off button
    """
    skinType = "CHECKOFF"
    value = False
    
    def __init__(self,textstring,pos=Vec2(0,0),size=Vec2(20,20),point=14,onClick=None):
        """ creates a check box """
        Button.__init__(self,"    "+textstring,pos,size,point,onClick)
        
    def onClick(self,button,key,mouse):
        """ checks or uncecks the button value """
        self.regenerate = True
        self.value = not self.value
        if self.value:
            self.skinType = "CHECKON"
        else:
            self.skinType = "CHECKOFF"  
 
class Icon(Button):
    """ a button that represents an image """
    
    skinType = None
    
    def __init__(self,pos=Vec2(0,0),size=Vec2(20,20),point=14,onClick=None):
        """ creates a clikcable icon object """
        Button.__init__(self,"",pos,size,point,onClick)
        
        
class Image(Widget):
    
    
    def __init__(self,path,pos=Vec2(0,0),size=Vec2(256,256)):
        """ create a gui lable """
        Widget.__init__(self,pos,size)
        self.texture = loader.loadTexture(path)
        cm = CardMaker('image')
        cm.setFrame(0,1,1,0)
        self.image = self.node.attachNewNode(cm.generate())
        self.image.setScale(self.size.getX(),1,self.size.getY())
        self.image.setTexture(self.texture)
        self.image.setTwoSided(True)
        self.image.setTransparency(True)
        
    def draw(self,pos,size):
        """ modifys the geometry of the object """
        #if self.regenerate:
        print self.size
        self.image.setScale(self.size.getX(),1,self.size.getY())
        gui.theme.fixZ(self)
    
