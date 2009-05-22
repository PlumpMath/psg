
# Player------------------------------------------------------------------------
class Player:
	name     = None
	_entities = []
	def __init__(self,  name="Player"):
		self.name = name
		
	def addEntity(self,  e):
		self._entities.append(e)
		e.setOwner(self)
		
	def delEntity(self,  e):
		try:
			self._entities.remove(entity)
		except:
			pass
