''' Serializable.py
	
	Author:			Chad Rempp
	Date:			2009/12/04
	License:		GNU LGPL v3 
	Todo:			I don't think __setstate__ works as expected!
'''

try:
	import cPickle as pickle
except:
	import pickle

class Serializable(object):
	''' Serializable object interface.
	
	A class that is serializable must define an attribute _sDataList which is
	a list of the names of the attributes (other than base types) that should
	be serialized.
	
	For example, if a class has an attribute named objectList which is a list
	that contains object instances the following would be needed:
	    _sDataList = ['objectList']
	
	If you are unsure if an attribute will be pickled it's probably safe to
	list it in the data list although this could effect performance since this
	could cause it to be pickled twice.
	'''
		
	_sDataList = []
	
	def __init__(self):
		pass
	
	def write(self, file):
		''' Pickle ourself and write to file. We must attach the file handle
		to the class so we can easily remove it before pickling.'''
		pStr = pickle.dumps(self)
		fh = open(file, 'w')
		fh.write(pStr)
		fh.close()
	
	def read(self, file):
		''' Read from file and unpickle ourself. Restoring of attributes is done
		in __setstate__ so we don't need the object returned from load.'''
		fh = open(file, 'r')
		pickle.load(fh)
		
	def __getstate__(self):
		''' Add __dict__ to our state and then cycle through the specified dat
		list.'''
		sDict = self.__dict__.copy()
		for s in self._sDataList:
			sDict[s]=eval('self.'+s)
		return sDict
		
	def __setstate__(self, state):
		''' Assign the contents of state back to ourself.'''
		self.__dict__ = state
		for s in self._sDataList:
			val = state[s]
			attr = eval('self.'+s)
			attr = val