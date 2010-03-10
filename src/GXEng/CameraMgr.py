''' CameraMgr.py
	
	Conrols camera movement.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			
'''

# Python imports
import math

# Panda imports
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Vec3

# PSG imports
import Event

class CameraManager(DirectObject):
	''' A class that controls the camera
		
		Internally positions must be represented by Vec3
	'''
	def __init__(self, fov=60.0, pos=(0,20,0), lookAt=(0,0,0), target=(0,0,0), dist=40):
		self.fov     = fov
		self.pos     = Vec3(pos)
		self.lookAt  = Vec3(lookAt)
		self.target  = Vec3(target)
		self.camDist = dist
		
		self.movingUp = False
		self.movingDown = False
		self.movingLeft = False
		self.movingRight = False
		self.dragging=False
		
		self.mx,self.my=0,0
		
	def startCamera(self):
		LOG.debug("Starting CameraManager")
		
		# Register with Dispatcher
		Event.Dispatcher().register(self, 'E_Mouse_3', self.startDrag)
		Event.Dispatcher().register(self, 'E_Mouse_3_Up', self.stopDrag)
		Event.Dispatcher().register(self, 'E_MouseWheel_Up', self.adjustCamDist)
		Event.Dispatcher().register(self, 'E_MouseWheel_Down', self.adjustCamDist)
		Event.Dispatcher().register(self, 'E_Key_CameraUp', self.keyMove)
		Event.Dispatcher().register(self, 'E_Key_CameraUp-up', self.keyMove)
		Event.Dispatcher().register(self, 'E_Key_CameraDown', self.keyMove)
		Event.Dispatcher().register(self, 'E_Key_CameraDown-up', self.keyMove)
		Event.Dispatcher().register(self, 'E_Key_CameraLeft', self.keyMove)
		Event.Dispatcher().register(self, 'E_Key_CameraLeft-up', self.keyMove)
		Event.Dispatcher().register(self, 'E_Key_CameraRight', self.keyMove)
		Event.Dispatcher().register(self, 'E_Key_CameraRight-up', self.keyMove)
		
		# Turn off default camera movement
		base.disableMouse()
		
		# Set camera properties
		base.camLens.setFov(self.fov)
		base.camera.setPos(self.pos)
		
		# The lookAt camera method doesn't work right at the moment.
		# This should be moved into a seperate method of Camera Manager anyway
		# so we can set this to the players start pos.
		#base.camera.lookAt(self.lookAt)
		
		self.turnCameraAroundPoint(0,0,self.target,self.camDist)
		
		taskMgr.add(self.dragTask,'dragTask')
		
	def turnCameraAroundPoint(self,tx,ty,p,dist):
		newCamHpr=Vec3()
		camHpr=base.camera.getHpr()
		newCamHpr.setX(camHpr.getX()+tx)
		newCamHpr.setY(camHpr.getY()-ty)
		newCamHpr.setZ(camHpr.getZ())
		
		base.camera.setHpr(newCamHpr)
		angleradiansX = newCamHpr.getX() * (math.pi / 180.0)
		angleradiansY = newCamHpr.getY() * (math.pi / 180.0)
		# HANG OCCURS HERE
		base.camera.setPos( dist*math.sin(angleradiansX)*math.cos(angleradiansY)+p.getX(),
						   -dist*math.cos(angleradiansX)*math.cos(angleradiansY)+p.getY(),
						   -dist*math.sin(angleradiansY)+p.getZ()  )
		
		base.camera.lookAt(p.getX(),p.getY(),p.getZ() )
		
	def setTarget(self,x,y,z):
		self.target.setX(x)
		self.target.setY(y)
		self.target.setZ(z)
		
	def startDrag(self, event):
		self.dragging=True
		
	def stopDrag(self, event):
		self.dragging=False
		
	def adjustCamDist(self, event):
		if event.type == 'E_MouseWheel_Up':
			aspect = 0.9
		elif event.type == 'E_MouseWheel_Down':
			aspect = 1.1
		self.camDist=self.camDist*aspect
		self.turnCameraAroundPoint(0,0,self.target,self.camDist)
		
	def dragTask(self,task):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse() 
			if self.dragging:
				self.turnCameraAroundPoint((self.mx-mpos.getX())*100,(self.my-mpos.getY())*100,self.target,self.camDist)       
			else:
				moveY=False
				moveX=False
				if self.my>0.8:
					angleradiansX = base.camera.getH() * (math.pi / 180.0)
					aspect=(1-self.my-0.2)*5
					moveY=True
				if self.movingUp:
					angleradiansX = base.camera.getH() * (math.pi / 180.0)
					aspect=(1-(0.95)-0.2)*5
					moveY=True
				if self.my<-0.8:
					angleradiansX = base.camera.getH() * (math.pi / 180.0)+math.pi
					aspect=(1+self.my-0.2)*5
					moveY=True
				if self.movingDown:
					angleradiansX = base.camera.getH() * (math.pi / 180.0)+math.pi
					aspect=(1+(-0.95)-0.2)*5
					moveY=True
				if self.mx>0.8:
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5
					aspect2=(1-self.mx-0.2)*5
					moveX=True
				if self.movingRight:
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5
					aspect2=(1-(0.95)-0.2)*5
					moveX=True
				if self.mx<-0.8:
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5
					aspect2=(1+self.mx-0.2)*5
					moveX=True
				if self.movingLeft:
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5
					aspect2=(1+(-0.95)-0.2)*5
					moveX=True
				if moveY:   
					self.target.setX(self.target.getX()+math.sin(angleradiansX)*aspect)
					self.target.setY(self.target.getY()-math.cos(angleradiansX)*aspect)
					self.turnCameraAroundPoint(0,0,self.target,self.camDist)
				if moveX:   
					self.target.setX( self.target.getX()-math.sin(angleradiansX2)*aspect2 )
					self.target.setY( self.target.getY()+math.cos(angleradiansX2)*aspect2 )
					self.turnCameraAroundPoint( 0,0,self.target,self.camDist )               
			self.mx=mpos.getX()
			self.my=mpos.getY()                               
		return task.cont
	
	def keyMove(self, event):
		if event.type == 'E_Key_CameraUp':
			self.movingUp = True
		elif event.type =='E_Key_CameraUp-up':
			self.movingUp = False
		elif event.type =='E_Key_CameraDown':
			self.movingDown = True
		elif event.type =='E_Key_CameraDown-up':
			self.movingDown = False
		elif event.type =='E_Key_CameraLeft':
			self.movingLeft = True
		elif event.type =='E_Key_CameraLeft-up':
			self.movingLeft = False
		elif event.type =='E_Key_CameraRight':
			self.movingRight = True
		elif event.type =='E_Key_CameraRight-up':
			self.movingRight = False
