"""

    This file holds complex controls
    that are composed of multiple widgets

"""
from widgets import *

class Holder(GUI,Widget):
    """ like a pane but does not clip its children """
    
    
    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100)):
        """ creates a holder """
        Widget.__init__(self,pos,size)
        self.things = []
     
    def add(self,thing):
        """ adds childred elements to the holder """
        self.things.append(thing)
        thing.reparentTo(self.node)
        thing.parent = self
        return thing
    
    def reSize(self):
        """ does nothing on resize """
    
    def reparentTo(self,node):
        """ reparents this holder to a node """
        self.node.reparentTo(node)
        
    def update(self):
        """ when it is opned """
    
    def do(self):
        """ every one in awhile """
      
    def draw(self,pos,size):
        """ draws the children of this holder """
        gui.theme.fixZ(self)
        GUI.draw(self,pos,size)
          
          
class Pane(Holder):
    
    """ pane is a holder that clips its elements """
        
    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100)):
        """ creates a pane """
        Widget.__init__(self,pos,size)
        self.things = []
        self.clipper = Clipper(self.pos,self.size)
        self.canvis = self.clipper.node()
        self.canvis.reparentTo(self.node)
        #self.canvis.setPos(0,0,10)
        self.clipper.resize()
    
    def add(self,thing):
        """ adds childred elements to the holder """
        self.things.append(thing)
        thing.reparentTo(self.canvis)
        thing.parent = self
        return thing
  
    def draw(self,pos,size):
        """ draws the children of this holder and clips them"""
        gui.theme.fixZ(self)
        self.clipper.pos = self.pos+pos
        self.clipper.size = self.size
        self.clipper.resize()
        GUI.draw(self,pos,size)

        
class Frame(Pane):
    
    """
        Frame has a frame border around it and no extra controls 
    """
    
    skinType = "FRAME"
    dropGeom = 0
    
    def draw(self,pos,size):
        """ update the frame represintaion """
        if self.geom == None or self.regenerate:
            if self.geom:
                self.geom.removeNode()
            if self.skinType:
                box = (self.skinType, Vec2(0,0),self.size,self)
                self.geom = gui.theme.generate(box)
                if self.geom:
                    self.geom.reparentTo(self.node)
                    self.geom.setZ(self.dropGeom)
        self.regenerate = False
        Pane.draw(self,pos,size)
        
    def mouseEvent(self,key,mouse):
        """ on mouse event pass it down to the children """
        Pane.mouseEvent(self,key,mouse)
        self.onClick(self,key,mouse)
        return True
        
    def onClick(self,button,key,mouse):
        """ frames consume mouse clicks """
        return False
  
class SlideVBar(Frame):
    """ 
        Vertical bar chart like button
    """
    skinType = None

    def __init__(self,*args,**kargs):
        if "onChange" in kargs:
            self.onChange = kargs["onChange"]
            del kargs["onChange"]
        Frame.__init__(self,*args,**kargs)
        self.w = self.add(Button("",pos=Vec2(0,0),size=self.size,onClick=self.onClick))
        self.w.skinType = "INPUT"
    
    def onClick(self,button,key,mouse):
        """ changes the value """
        self.setValue((self.size[1]-mouse.getY())/self.size.getY()) 
    
    def setValue(self,value):
        """ sets the value of the slide button """
        self.value = value
        #self.setText(str(int(value))+"%")
        self.w.size.setY(value*self.size.getY())
        self.w.pos.setY(self.size[1] - value*self.size.getY())
        self.w.setPos(self.w.pos) 
        self.w.regenerate = True
        gui.redraw()        
        self.onChange(self)
        
    def onChange(self,button):
        """ overide this method to get the change event """
        
        
class SlideHBar(Frame):
    """ 
        Horizontal bar chart like button
    """
        
    skinType = None

    def __init__(self,*args,**kargs):
        if "onChange" in kargs:
            self.onChange = kargs["onChange"]
            del kargs["onChange"]
        Frame.__init__(self,*args,**kargs)
        self.w = self.add(Button("",pos=Vec2(0,0),size=self.size,onClick=self.onClick))
        self.w.skinType = "INPUT"
    
    def onClick(self,button,key,mouse):
        """ changes the value """
        self.setValue(mouse.getX()/self.size.getX()) 
    
    def setValue(self,value):
        """ sets the value of the slide button """
        self.value = value
        #self.setText(str(int(value))+"%")
        self.w.size.setX(value*self.size.getX()) 
        self.w.regenerate = True
        gui.redraw()
        self.onChange(self)
        
    def onChange(self,button):
        """ overide this method to get the change event """
        
class VScroll(Frame):
    """ 
        Vertical scroll bar
    """
    
    def __init__(self,pos=Vec2(0,0),size=Vec2(10,100)):
        Frame.__init__(self,pos,size)
        self.skinType = "INPUT"
        self.up = self.add(Button("",pos=Vec2(0,0),size=Vec2(10,10),onClick=self.scrollUp))
        self.down = self.add(Button("",pos=Vec2(0,size[1]-10),size=Vec2(10,10),onClick=self.scrollDown))
        self.center = self.add(Button("",pos=Vec2(0,size[1]/2-10),size=Vec2(10,10)))
        self.center.onClick = self.onCenterDrag
        self.up.skinType = "INPUT"
        self.down.skinType = "INPUT"
        self.center.skinType = "INPUT"
        self.value = .5
        
    def onCenterDrag(self,button,key,mouse):
        self.center.onDrag(button,key,mouse)
        gui.dragFun = self.onScrollBase
        
    def scrollUp(self,*args):
        self.center.pos += Vec2(0,-10)
        self.onScrollBase()
                
    def scrollDown(self,*args):
        self.center.pos += Vec2(0,10)
        self.onScrollBase()
        
    def onScrollBase(self,*args):
        value = min(self.size[1],max(0,self.center.pos[1]))/float(self.size[1])
        self.center.setPos(Vec2(0,value*self.size[1]))
        if abs(self.value - value) > .05:
            print "blink"
            self.onScroll(value)
            self.value = value
            self.center.regenerate=True
            gui.redraw()
    
    def onScroll(self,value):
        pass
        
class HScroll(Frame):
    
    """ 
        Horizontal scroll bar
    """
    
    def __init__(self,pos=Vec2(0,0),size=Vec2(10,100)):
        Frame.__init__(self,pos,size)
        self.skinType = "INPUT"
        self.up = self.add(Button("",pos=Vec2(0,0),size=Vec2(10,10),onClick=self.scrollUp))
        self.down = self.add(Button("",pos=Vec2(size[0]-10,0),size=Vec2(10,10),onClick=self.scrollDown))
        self.center = self.add(Button("",pos=Vec2(size[0]/2-10,0),size=Vec2(10,10)))
        self.center.onClick = self.onCenterDrag
        self.up.skinType = "INPUT"
        self.down.skinType = "INPUT"
        self.center.skinType = "INPUT"
        self.value = .5
        
    def onCenterDrag(self,button,key,mouse):
        self.center.onDrag(button,key,mouse)
        gui.dragFun = self.onScrollBase
        
    def scrollUp(self,*args):
        self.center.pos += Vec2(-10,0)
        self.onScrollBase()
                
    def scrollDown(self,*args):
        self.center.pos += Vec2(10,0)
        self.onScrollBase()
        
    def onScrollBase(self,*args):
        value = min(self.size[0],max(0,self.center.pos[0]))/float(self.size[0])
        self.center.setPos(Vec2(value*self.size[0],1))
        if abs(self.value - value) > .05:
            self.onScroll(value)
            self.value = value
            self.center.regenerate=True
            gui.redraw()        
        
    def onScroll(self,value):
        pass
        
class ScrollPane(Holder):
    """ 
        This is used to put stuff inside and scroll around them
    """
    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100)):
        Holder.__init__(self,pos,size)
        self.h = self.add(HScroll(Vec2(0,size[1]-10),size=Vec2(size[0]-10,10)))
        self.v = self.add(VScroll(Vec2(size[0]-10,0),size=Vec2(10,size[1]-10)))
        self.p = self.add(Pane(Vec2(0,0),size=Vec2(size[0]-10,size[1]-10)))
        self.h.onScroll = self.onHScroll
        self.v.onScroll = self.onVScroll
        self.add = self.p.add
        
    def onHScroll(self,value):
        for thing in self.p.things:
            print self.h.value,value
            thing.pos += Vec2(self.h.value*100,0)
            thing.pos -= Vec2(value*100,0)
            thing.setPos(thing.pos)
            thing.regenerate=True
        gui.redraw() 
        
    def onVScroll(self,value):
        for thing in self.p.things:
            thing.pos += Vec2(0,self.v.value*100)
            thing.pos -= Vec2(0,value*100)
            thing.setPos(thing.pos)
            thing.regenerate=True
        gui.redraw() 
        
class Form(Frame):
    """
        This is the standard window of the windowing system
        use this as the top holder for most of the controls
        this should be added to the main gui object
    
    """
    skinType = "FORM"
    dropGeom = 20
    
    def __init__(self,title,pos=Vec2(200,200),size=Vec2(200,300)):
        Frame.__init__(self,pos,size)
        self.minSize = Vec2(100,30)
        self.things = []
        self.title = title
        self.bar = Frame.add(self,Button(self.title,
            pos=Vec2(20,0),
            size=Vec2(min(200,self.size[0]-40),20),
            onClick=self.startDrag));
        self.x = Frame.add(self,Button("",pos=Vec2(self.size[0]-20,0),size=Vec2(20,20),onClick=self.onClose));
        self.x.skinType = "X"
        self.bar.skinType = "FRAMEBAR"
        self.sizer = Frame.add(self,Button("",pos=self.size-Vec2(20,20),size=Vec2(20,20),onClick=self.startResize));
        self.sizer.skinType = "DRAG"
        
    def startDrag(self,button,key,mouse):
        self.onDrag(button,key,mouse+Vec2(+20,0))

    def startResize(self,button,keys,mouse):
        """ called when the form is begining to be reized """
        self.sizer.onDrag(button,keys,mouse)
        gui.dragFun = self.onResize
        
    def onClose(self,button,key,mouse):
        """ called when the form is closing """
        self.node.hide()
        
    def setSize(self,size):
        self.size = size
        self.bar.size = Vec2(min(200,self.size[0]-40),10)
        self.sizer.setPos( self.size-Vec2(20,20) )
        self.x.setPos( Vec2(self.size[0]-20,0) )
        Frame.setSize(self,size)
        
    def onResize(self):
        """ called when the form should resize """
        delta = self.size - (self.sizer.pos+Vec2(20,20))
        self.size = self.sizer.pos+Vec2(20,20)
        if self.size[0] < self.minSize[0]:
            self.size.setX(self.minSize[0])
        if self.size[1] < self.minSize[1]:
            self.size.setY(self.minSize[1])
        self.bar.size = Vec2(min(200,self.size[0]-40),10)
        self.sizer.setPos( self.size-Vec2(20,20) )
        self.x.setPos( Vec2(self.size[0]-20,0) )
        #self.sizer.pos=self.size-Vec2(10,10)
        if delta.length() > 1:
            self.regenerate = True
            gui.redraw()

    def toggle(self):
        """ hids or shows this thing """
        if self.node.isHidden():
            self.node.show()
        else:
            self.node.hide()


class GridForm(Form):
    
    """
        This quickly created crud like interfaces with 
        descrition on one side and and widgets on the other
    """
    
    def __init__(self,title,pos=Vec2(300,200),size=Vec2(200,300)):
        Form.__init__(self,title,pos,size)
        self.currentY = 30
        
    def add(self,lable,thing):
        """ requires a lable when adding a widgit """
        thing = Frame.add(self,thing)
        thing.pos = Vec2(100,self.currentY)
        thing.setPos(thing.pos)
        label = Frame.add(self,Lable(lable,pos=Vec2(0,self.currentY)))
        self.currentY+=20
        #self.size = Vec2(300,max(100,self.currentY+20))
        #self.sizer.setPos( self.size-Vec2(20,20) )
        #self.onResize() 
        #self.regenerate = True
        #gui.redraw()
        return thing


class Menu(Frame):
    """
        Creates an interesting style menu that has all of its drop downs horisontal        
    """
    skinType = None
    
    def __init__(self,title,options,pos=Vec2(0,0),size=Vec2(200,300)):
        """ options are in a form of  name,funciton,arguments """
        Frame.__init__(self,pos,Vec2(160,10+20*len(options)))
        self.options = options
        i = 0
        for (name,fun,args) in self.options:
            button = Button(name, Vec2(0,10+int(i)*20),Vec2(160,16),onClick=self.menuSelect)
            self.add(button)
            i += 1
         
    def menuSelect(self,button,keys,mouse):
        """ called when one of the menus have been selected """
        for (name,fun,args) in self.options:
            if button.getText() == name and fun:
                fun(*args)
                 
