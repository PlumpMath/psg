from pandac.PandaModules import *
from random import random as r

from theme import Theme
import time

class GUI:
    indent = 0
    def __init__(self,keys,theme=Theme):
        import __builtin__
        __builtin__.gui = self
        self._setupBase()
        base.accept('aspectRatioChanged', self._reSize )
        
        self.keys = keys
        self.things = []
        self.node = NodePath(self.__class__.__name__)
        self.node.reparentTo(aspect2d)
        self.drag = None
        self.dragPos = Vec2(0,0)
        try:
            self.theme = theme()
        except AttributeError:
             self.theme = theme
        self.pos = Vec2(0,0)
        self.mouse = Vec2(0,0) 
        self.node.setBin("fixed",2)
        self.node.setDepthWrite(False)
        self.node.setDepthTest(False)
        self.dragFun = None
        self.parent = False
        self.lastDragMoue = Vec2(0,0)    
        self.lastTime = time.time()
        self.refit = []
        taskMgr.add(self.guiTask,'gui task')
        self.to2d = To2D()
     
    def _setupBase(self):
        """ initilizes the window """
        self.windowsize = 800, 600
        self.aspect  = float(self.windowsize[0]) / float(self.windowsize[1])            
        self._reSize()
        
        
    def toggle(self):
        if self.node.isHidden():
            self.node.show()
        else:
            self.node.hide()
              
    def guiTask(self,task):
        
        now = time.time() 
        if now - self.lastTime > 1.0:
            self.lastTime = now 
            self.update() 
        
        if self.drag:
             
            md = base.win.getPointer( 0 )
            x = md.getX()
            y = md.getY()
            mouse = Vec2(x,y)
            print mouse
            if (self.lastDragMoue - mouse).length() < 2:
                return task.cont# moved less then 1 px
            self.lastDragMoue = mouse
                   
            parent = self.drag.parent
            offset = Vec2(0,0)
            while parent:
                offset += parent.pos
                parent = parent.parent
            self.drag.pos = self.dragPos+mouse
            self.drag.node.setPos(self.drag.pos[0],0,self.drag.pos[1])
            
            if self.dragFun:
                self.dragFun()
            
            self.redraw()
            
        else:
            self.drugFun = False
            
        if self.keys.focus:
            pass
#             ls = LineSegs()
#             ls.setColor(0.0, 0.0, 0.0, 1.0)
#             ls.moveTo(0.0, 0.0, -0.15 * line_height)
#             ls.drawTo(0.0, 0.0, 0.70 * line_height)
#             attach_new_node(ls.create())
            
        return task.cont
        
    def add(self,thing):
        self.things.append(thing)
        thing.reparentTo(self.node)
        thing.parent = self
        self.redraw()
        return thing
                
    def toFront(self,thing):
        self.things.remove(thing)
        self.things.append(thing)
    
          
    def tile(self):
        
        current = Vec2(100,1000)
        columnWidth = 0
        for thing in self.things:
            if current[0]+thing.size.getY()+20 > self.windowsize[0]:
                current.setY(0)
                current.setX(columnWidth)
                columnWidth = 0
                
            thing.setPos(current)
            current.setY(current.getY()+thing.size.getY()+20)
            columnWidth = max(columnWidth,thing.size.getX()+20)
           
        self.redraw()
                
    def reSize(self,windowsize=None):
        if windowsize:
            for thing in self.things:
                thing.resize()
                
            self.node.reparentTo(aspect2d)
            self.windowsize = windowsize   
            self.redraw() 
            
            for thing in self.refit:
                thing.onRefit(windowsize) 
    
    def addOnRefit(self,thing):
        self.refit.append(thing)
                
    def baseMouseEvent(self,key):
        #self.node.ls()
        md = base.win.getPointer( 0 )
        x = md.getX( )
        y = md.getY( )
        self.mouse = Vec2(x,y)
        GUI.indent = 0
        m = self.mouseEvent(key,self.mouse)        
        self.redraw()
        return m
        
    def redraw(self):
        self.theme.resetZ()
        self.draw(Vec2(0,0),Vec2(4000,2000))
       
    def mouseEvent(self,key,mouse):
        GUI.indent += 1
        #print " "*GUI.indent,"children:",len(self.things)
        for thing in reversed(self.things):
            #print " "*GUI.indent, thing, mouse
            #print " "*GUI.indent, thing.pos[0] ,"<", mouse[0] ,"<", thing.pos[0]+thing.size[0] 
            #print " "*GUI.indent, thing.pos[1] ,"<", mouse[1] ,"<", thing.pos[1]+thing.size[1]
            if not thing.node.isHidden() and (
                    thing.pos[0] < mouse[0] and mouse[0] < thing.pos[0]+thing.size[0] and
                    thing.pos[1] < mouse[1] and mouse[1] < thing.pos[1]+thing.size[1] ) :
                #print "-"*GUI.indent+">", thing, mouse
                if thing.mouseEvent(key,mouse-thing.pos):
                    #print " "*GUI.indent," used:",thing
                    return True
        GUI.indent -= 1
        gui.keys.focus = None
        return False
     
    def draw(self,pos,size):
        for thing in self.things:
            thing.draw(self.pos+pos,size)
    
    def update(self):
        for thing in self.things:
            if not thing.node.isHidden():
                thing.update()
        
    def _reSize(self):
        """ resize the windwo """
        aspect2d.setScale(2./self.windowsize[0], 1, -2./self.windowsize[1])
        aspect2d.setPos(-1, 0, 1)
        aspect2d.reparentTo(render2d)
        pl = PerspectiveLens()
        pl.setFar(2000)
        pl.setNear(.01)
        pl.setAspectRatio(self.aspect) 
        base.cam.node().setLens(pl)
        base.cam.node().setCameraMask(BitMask32.bit(0))
        
class Clipper:
    
    def __init__(self,pos=Vec2(0,0),size=Vec2(100,100)):
        self.pos = pos
        self.size = size
        self._canvas_node = NodePath("inside")
        
    def resize(self):
        r = Vec3.right();
        u = Vec3.up();
        windowsize = gui.windowsize
        clip_frame = [ self.pos[0],self.pos[1],self.size[0],self.size[1]]
        _clip_frame = [0,0,0,0]
        _clip_frame[0] = clip_frame[0]/float(windowsize[0]/2)-1
        _clip_frame[3] = -clip_frame[1]/float(windowsize[1]/2)+1 
        _clip_frame[1] = (clip_frame[2]+clip_frame[0])/float(windowsize[0]/2)-1
        _clip_frame[2] = -(clip_frame[3]+clip_frame[1])/float(windowsize[1]/2)+1
        self._clip_plane_node = PandaNode("tmp node")
        left_clip = PlaneNode("left_clip", Plane(r, Point3(r * _clip_frame[0])))
        top_clip =  PlaneNode("top_clip", Plane(-u, Point3(u * _clip_frame[3])))
        right_clip = PlaneNode("right_clip", Plane(-r, Point3(r * _clip_frame[1])))
        bottom_clip = PlaneNode("bottom_clip", Plane(u, Point3(u * _clip_frame[2])))
        self._clip_plane_node.removeAllChildren();
        self._clip_plane_node.addChild(left_clip);
        self._clip_plane_node.addChild(right_clip);
        self._clip_plane_node.addChild(bottom_clip);
        self._clip_plane_node.addChild(top_clip);
        plane_attrib = ClipPlaneAttrib.make();
        plane_attrib = plane_attrib.addOnPlane(NodePath.anyPath(left_clip))
        plane_attrib = plane_attrib.addOnPlane(NodePath.anyPath(right_clip))
        plane_attrib = plane_attrib.addOnPlane(NodePath.anyPath(bottom_clip))
        plane_attrib = plane_attrib.addOnPlane(NodePath.anyPath(top_clip))
        self._canvas_node.setAttrib(plane_attrib);
        #_canvas_node.reparentTo(aspect2d)
        
    def node(self):
        return self._canvas_node    


class To2D:    
    """ class that can take all the things 
        that where added to it and manipulate 
        them in 2d guish kinda way """
    
    def __init__(self):
        self.things = []
        self.boxes = []
        
    def clear(self):
        """ clear all 3d things in 2d pane """
        self.things = []
        self.boxes = []
        
    def add(self,thing):
        """ add a new 3d thing in 2d pane """
        self.things.append(thing)
        
    def remove(self,thing):
        """remove thing from gui"""
        self.things.remove(thing)
    
    def getGUIPos(self,node):        
        """ node -> pos on screen , -100,-100 it its not on screen"""
        pos2d = self.compute2dPosition(node,Vec3(0,0,0))
        if pos2d:
            size = 1/base.cam.getRelativePoint(node,Point3(0, 0, 0)).length()
            return Point2((pos2d[0]+1)*game.windowsize[0]/2, (-pos2d[1]+1)*game.windowsize[1]/2),size
        return Point2(-100,-100),0
        
    def makeBoxes(self):
        """ make a box for every thing """
        for thing in self.things:
            pos2d = self.compute2dPosition(thing.node,Vec3(0,0,0))
            if pos2d:
                pos2d = Point2((pos2d[0]+1)*game.windowsize[0]/2, (-pos2d[1]+1)*game.windowsize[1]/2)
                f =  DirectFrame( relief = DGG.FLAT
                          ,frameColor = (200, 200, 200, 0.85), scale=1
                          ,frameSize = (pos2d[0],pos2d[0]+10,pos2d[1],pos2d[1]+10))
                self.boxes.append(f)
                  
    def getThingInGUIRec(self,rec):
        """ is there a thing in any of the rectagle """
        sx,ex,sy,ey = rec      
        if sx > ex: sx,ex = ex,sx
        if sy > ey: sy,ey = ey,sy
        things = []
        for thing in self.things:
            pos2d = self.compute2dPosition(thing.node,Vec3(0,0,0))
            if pos2d:
                pos2d = Point2((pos2d[0]+1)*game.windowsize[0]/2, (-pos2d[1]+1)*game.windowsize[1]/2)
                x,y=pos2d[0],pos2d[1]
                if sx < x and x < ex and sy < y and y < ey :
                    things.append(thing)                    
        return things       
               
    def compute2dPosition(self,nodePath, point = Point3(0, 0, 0)):
        """ Computes a 3-d point, relative to the indicated node, into a
        2-d point as seen by the camera.  The range of the returned value
        is based on the len's current film size and film offset, which is
        (-1 .. 1) by default. """
        p3d = base.cam.getRelativePoint(nodePath, point)
        p2d = Point2()
        if base.cam.node().getLens().project(p3d, p2d):
            return p2d
        return None 

    