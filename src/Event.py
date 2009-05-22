from datetime import datetime
import weakref
from Util import Singleton

# Event-------------------------------------------------------------------------
class Event(object):
	type            = 'Generic'
	source          = None
	data            = None
	_eventtime      = datetime.now()
	_defaulthandler = None
	#_arglist        = []	
	
	def __init__(self,  type,  src=None, data=None,  defaulthandler=None):
		self.type = type
		self._defaulthandler = defaulthandler
		self.source = src
		self.data   = data
		
	def __repr__(self):
		return '<EVENT: ' + self.type + ' from: ' + str(self.source) + ' at:' + str(self._eventtime) + '>'


class Dispatcher:
	''' Dispatcher class.
		This is a singleton so only one instance will exist.
		The listeners are stored in a dictionary called _listeners. Each key
		is a string representing an event. Each value is a list of tuples
		(listenerObject, handler). The _listener dictionary contains references
		to objects that will prevent garbage collection so they must be unregistered
		(weakref won't work with tuple values.'''
	__metaclass__=Singleton
	_eventlist = ['E_All',
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
						'E_EndTurn',
						'E_ExitGame',
						'E_ExitProgram']
	_listeners = {}
	
	def __init__(self):
		''' Set up the listener dictionary by creating keys for each event.'''
		for e in self._eventlist:
			self._listeners[e]=[]
		
	def register(self, listener, event, handler):
		''' Register an event with the dispatcher.
				listener is the object to register, event is the string representation
				of the event and handler is the method to call when the event occurs.
				TODO - Add support for handler arguments.'''
		#print("registering - " + str(listener))
		if event in self._eventlist:
			self._listeners[event].append([listener,handler])
		else:
			print("Error: Event %s doesn't exist"%event)
			
	def unregister(self, listener, event=None):
		''' Unregister the given listener from the dispatcher. If an event is
			given only unregister from that event.'''
		def removeFromEvent(e, l):
			for tup in self._listeners[e]:
				if tup[0] == l:
					self._listeners[e].remove(tup)
		if event is not None:
			removeFromEvent(event, listener)
		else:
			for e in self._eventlist:
				print e
				removeFromEvent(e, listener)
		
	def broadcast(self, event):
		''' Handle event for each listener registered to hear the event type.
			The E_All event always needs to be run through.
			TODO - Check if there's a problem with duplicate event handling due
			       to the E_All.'''
		print("Broadcasting: %s"%str(event))
		if event is not None and event.type in self._listeners.keys():
			for l in self._listeners[event.type]:
				instance  = l[0]
				classtype = l[0].__class__
				handler   = l[1]
				handler.__get__(instance,classtype)(event)
			for l in self._listeners['E_All']:
				instance  = l[0]
				classtype = l[0].__class__
				handler   = l[1]
				handler.__get__(instance,classtype)(event)
		else:
			print("Error: Event %s doesn't exist"%str(event))
