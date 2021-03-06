"""

    The drawer tries to draw the ui in as little goems 
    and triangles as possible
    
    It tries to use only a single vertex buffer and only 
    a single texture
    
    It clips polygons in software rather then resorting to 
    scissor tests or clip planes which reduces trips to the card
    and speeds stuff up.

"""

from pandac.PandaModules import *
import os



from random import *
def randVec():
    """ reandom vector """
    return Vec3(random()-.5,random()-.5,random()-.5)


from game.GUI.Treegui.eggatlas import EggAtlas

from game.GUI.Treegui.theme import Stretch




class Drawer:

    def __init__(self):
        """ create the drawer """
        vfs = VirtualFileSystem.getGlobalPtr()
        
        self.atlas = EggAtlas(gui.theme.ATLAS)
        
        self.image = loader.loadTexture(gui.theme.TEXTURE)
        self.image.setCompression(Texture.CMOff)
        self.image.setMinfilter(Texture.FTNearest)
        self.image.setMagfilter(Texture.FTLinear)
        self.image.reload()

        self.drawer = self.makeThemeDrawer(gui.node)
        
        self.w = float(self.image.getXSize())
        self.h = float(self.image.getYSize())

        self.color = Vec4(1,1,1,1)

    def makeDrawer(self,node):
        """
            make generic 2d drawer 
        """
        drawer = MeshDrawer2D()
        drawer.setBudget(3000)

        drawerNode = drawer.getRoot()
        drawerNode.reparentTo(node)
        drawerNode.setDepthWrite(False)
        drawerNode.setTransparency(True)
        drawerNode.setTwoSided(True)
        drawerNode.setBin("fixed",0)
        drawerNode.setLightOff(True)
        drawerNode.node().setBounds(OmniBoundingVolume())
        drawerNode.node().setFinal(True) 
        
        # debug wire frame
        #cc = drawerNode.copyTo(node)
        #cc.setRenderModeWireframe()

        return drawer

    def makeThemeDrawer(self,node):
        """
            make the theme drawer
        """
        themeDrawer = self.makeDrawer(node)
        themeDrawer.getRoot().setTexture(self.image)
        return themeDrawer


    def draw(self,children):
        """ draws all of the children """
        self.clip = [(0,0,gui._width+100, gui._height+100)]

        self.drawer.setClip(0,0,gui._width+100, gui._height+100)
        
        self.drawer.begin()
        z = 0
        for child in reversed(children):
            z += 1
            self.drawChild(0,0,z,child)
            
        self.drawer.end()
        
    def drawChild(self,x,y,z,thing):
        """ draws a single thing """
        self.z = z
        
        
        
        if not thing.visable:
            return 
        
        
        self.color = Vec4(*thing.color)
        
        realX = x+float(thing._x)
        realY = y+float(thing._y)
        
        if thing.style:
            style = gui.theme.define(thing.style)
            if style:
                style.draw(
                    self,
                    (realX,realY),
                    (float(thing._width),float(thing._height)))
        
        if thing.clips:
            # set clip stuff
            self.pushClip(realX,realY,realX+thing._width,realY+thing._height)
            
        if thing.icon:
            rect = self.atlas.getRect(thing.icon)
            if rect: 
                self.color = thing.color
                u,v,us,vs = rect
                self.rectStreatch((realX,realY,us,vs),(u,v,us,vs))
            
        if thing.text:
            # draw text stuff
            if thing.editsText:
                self.drawEditText(
                    gui.theme.defineFont(thing.font),
                    thing.text,
                    realX,
                    realY,
                    thing.selection,
                    thing.caret)
            else:
                self.drawText(
                    gui.theme.defineFont(thing.font),
                    thing.text,
                    realX,
                    realY)
           
            
        if thing.children:
            for child in thing.children:
                z += 1
                self.drawChild(realX,realY,z,child)
                
        if thing.clips:
            self.popClip()
    
     
    
    def drawText(self, font, text, x, y):
        """ 
            draws just text
        """
        self.color = Vec4(*font.color)
        
        name =  font.name
        ox = x
        baseLetter = self.atlas.getChar(name + str(ord("T")))
        omaxh = baseLetter[3] - baseLetter[4][1]

        for line in text.split("\n"):
            build = []
            maxh = omaxh  
                
            for c in line:
                code = ord(c)            
                if code <= 32:
                    u,v,w,h,e = self.atlas.getChar(name + str(77))
                    x += e[0]
                    continue
                u,v,w,h,e = self.atlas.getChar(name + str(code))
                build.append((x,y+e[1],u,v,w,h))
                x += e[0]
                maxh = max(maxh,h-e[1])
                 
            for x,y,u,v,w,h in build:
                self.rectStreatch((x,y+maxh-h,w,h),(u,v,w,h))
                
            x = ox     
            y += maxh
    
    def drawEditText(self, font, text, x, y, selection=(0,0), caret=-1):
        """ 
            draws the text
            and selection
            and caret
        """
        self.color = Vec4(*font.color)
        name =  font.name
        
        char_count = 0 
        ox = x
        baseLetter = self.atlas.getChar(name + str(ord("T")))
        omaxh = baseLetter[3] - baseLetter[4][1]

        for line in text.split("\n"):
            build = []
            maxh = omaxh  
                
            for c in line:
                if char_count == caret:
                     u,v,w,h,e = self.atlas.getChar(name + str(ord('|')))
                     build.append((x-w/2,y+e[1],u,v,w,h))
                char_count += 1 
                
                code = ord(c)            
                if code <= 32:
                    u,v,w,h,e = self.atlas.getChar(name + str(77))
                    x += e[0]
                    continue
                u,v,w,h,e = self.atlas.getChar(name + str(code))
                build.append((x,y+e[1],u,v,w,h))
                x += e[0]
                maxh = max(maxh,h-e[1])
            
            else:
                if char_count == caret:
                     u,v,w,h,e = self.atlas.getChar(name + str(ord('|')))
                     build.append((x-w/2,y+e[1],u,v,w,h))
                char_count += 1 
                 
            for x,y,u,v,w,h in build:
                self.rectStreatch((x,y+maxh-h,w,h),(u,v,w,h))
                
            x = ox     
            y += maxh    
        
    def rect(self,(x,y,xs,ys),(u,v)):
        """ draw a rectangle """
        us = xs
        vs = ys
        self.rectStreatch((x,y,xs,ys),(u,v,us,vs))
        
        
    def popClip(self):
        self.clip.pop()
        xs,ys,xe,ye = self.clip[-1]
        self.drawer.setClip(xs,ys,xe-xs,ye-ys)
            
    def pushClip(self,xs,ys,xe,ye):
        bxs,bys,bxe,bye = self.clip[-1]
        
        xs = max(bxs,xs)
        ys = max(bys,ys)
        xe = min(bxe,xe)
        ye = min(bye,ye)
        
        self.clip.append((xs,ys,xe,ye))   
        
        self.drawer.setClip(xs,ys,xe-xs,ye-ys)

    def rectStreatch(self,(x,y,xs,ys),(u,v,us,vs)):
        """ draw a generic stretched rectangle """
        # do clipping now:
        
        color = Vec4(1,1,1,1)
        
        w = self.w
        h = self.h
        
        u,v,us,vs = u/w,1-v/h,(u+us)/w,1-(v+vs)/h
        
        self.drawer.rectangle( 
            x,y,xs,ys,
            u,v,us-u,vs-v,
            #u/self.w,v/self.h,us/self.w,vs/self.h,
            color)


