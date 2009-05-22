class Singleton(type):
	''' Singleton Design Pattern (Recipe 412551)
		This ensures that only one instance of the class is ever created.
		It is possible to access Singletons by just calling the class name, eg:
		Singleton().function()'''
	def __init__(self, *args):
		type.__init__(self, *args)
		self._instances = {}

	def __call__(self, *args):
		if not args in self._instances:
			self._instances[args] = type.__call__(self, *args)
		return self._instances[args]

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
