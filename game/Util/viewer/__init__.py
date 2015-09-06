''' Utility classes and functions.
	
	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			
	
	These are helpful functions and classes that don't fit neatly into any other
	module.
	
'''

def frange(start, end=None, inc=None):
    '''A range function, that does accept float increments...'''

    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L

def getAvailableMaps():
	''' Reload the list of available maps.'''
	self.availableMaps = {}
	for mapFile in Map.getMapFiles():
		fh = open(Map.MAP_PATH + mapFile, 'rb')
		map = cPickle.load(fh)
		self.availableMaps[mapFile] = map.name