''' Editor.py
	
	The game map editor. Or at least it will be.

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3 
	Todo:			Finish
'''

import os, sys, time, wx
from pandac.PandaModules import WindowProperties, loadPrcFileData
loadPrcFileData("", "window-type none")

class P3dWxWindow(wx.Frame):
	def __init__(self, *args, **kw):
		wx.Frame.__init__(self, None, -1, *args, **kw)
	
	def getP3DSurface(self):
		return self.GetHandle()
	def getP3DSurfaceSize(self):
		return self.GetClientSizeTuple()

class PlayerFrame(wx.Frame):
	def __init__(self, parent, id, title):
		# First, call the base class' __init__ method to create the frame
		wx.Frame.__init__(self, parent, id, title)
		
		# Associate some events with methods of this class
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_MOVE, self.OnMove)
		
		panel = wx.Panel(self, -1)
		
		self.panel = panel
		
		sizer = wx.FlexGridSizer(2, 2, 5, 5)
		
		import Player
		import re
		
		p = re.compile('__\w+__')
		
		for attr in Player.Player.__dict__:
			if (type(Player.Player.__dict__[attr]) != 'function') and not(p.match(attr)):
				sizer.Add(wx.StaticText(panel, -1, attr+":"))
				sizer.Add(wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY))

		border = wx.BoxSizer()
		border.Add(sizer, 0, wx.ALL, 15)
		panel.SetSizerAndFit(border)
		self.Fit()


	# This method is called by the System when the window is resized,
	# because of the association above.
	def OnSize(self, event):
		size = event.GetSize()
		self.sizeCtrl.SetValue("%s, %s" % (size.width, size.height))

		# tell the event system to continue looking for an event handler,
		# so the default handler will get called.
		event.Skip()

	# This method is called by the System when the window is moved,
	# because of the association above.
	def OnMove(self, event):
		pos = event.GetPosition()
		self.posCtrl.SetValue("%s, %s" % (pos.x, pos.y))

import direct.directbase.DirectStart
class P3dWxApp(wx.App):
	
	def OnInit(self):
		#prepare and start the p3d-wx hybrid-engine mainloop
		self.wxevt_loop = wx.EventLoop()
		self.wxevt_old_loop = wx.EventLoop.GetActive()
		wx.EventLoop.SetActive(self.wxevt_loop)
		base.taskMgr.add(self._mainLoop, "MainLoopTask")
		
		#instantiate and assign the wx UI object
		self.win = P3dWxWindow(size=wx.Size(640, 480))
		self.SetTopWindow(self.win)
		
		#show the wx window
		self.win.Show(True)
		# is essential to let make up wx window before P3D stuff
		self._mainLoop()
		
		#bind wx events
		self.win.Bind(wx.EVT_SIZE, self.onSize)
		self.win.Bind(wx.EVT_CLOSE, self.onClose)
		self.vetoActivate=False
		self.win.Bind(wx.EVT_ACTIVATE, self.onActivate)
		
		#open the p3d window undecorated to use in the wx frame window
		wp=WindowProperties().getDefault()
		wp.setUndecorated(True)
		wp.setOpen(True)
		wp.setParentWindow(self.win.getP3DSurface())
		wp.setOrigin(0,0)
		wp.setForeground(True)
		wp.setSize(*self.win.getP3DSurfaceSize())
		print ">>>opening p3dsurface"
		assert base.openDefaultWindow(props=wp) == True
		#
		return True
	
	def _mainLoop(self, task = None):
		while self.wxevt_loop.Pending(): self.wxevt_loop.Dispatch()
		self.ProcessIdle()
		if task != None: return task.cont
	
	def onSize(self, event=None):
		'''to resize P3d Surface accordingly to his wx window container and to re-gain keyboard focus
		'''
		wp0=base.win.getProperties()
		if not wp0.getOpen():
			print ">>>[app onSize] win wasn't open: lets quit!"
			return
		wp=WindowProperties()
		wp.addProperties(wp0)
		wp.setSize(*self.win.getP3DSurfaceSize())
		wp.setForeground(True)
		base.win.requestProperties(wp)
		if event != None: event.Skip()
	
	def p3dSurfaceFocus(self):
		'''re-gain keyboard focus
		NOT
		'''
		wp=WindowProperties()
		wp.setForeground(True)
		base.win.requestProperties(wp)
		print ">>>p3d surface try to re-gain focus - do keyboard events still work?"
	
	def onActivate(self, evt=None):
		'''
		force focus to p3d surface expec. to get keyboard control back
		'''
		if self.vetoActivate:
			print (">>>[onActivate] veto!")
			evt.Skip()
		else:
			if evt.GetActive():
				print (">>>[onActivate] win ACTIVE")
				self.p3dSurfaceFocus()
				evt.Skip()
			else:
				print (">>>[onActivate] win IN-ACTIVE")
				evt.StopPropagation()
	
	def onClose(self, event):
		while self.wxevt_loop.Pending(): self.wxevt_loop.Dispatch()
		self.win.Destroy()
		try: base.userExit()
		except: sys.exit()

# Every wxWidgets application must have a class derived from wx.App
class MyApp(wx.App):
	# wxWindows calls this method to initialize the application
	def OnInit(self):
		# Create an instance of our customized Frame class
		frame = PlayerFrame(None, -1, "This is a test")
		frame.Show(True)
		
		# Tell wxWindows that this is our main window
		self.SetTopWindow(frame)
		
		# Return a success flag
		return True