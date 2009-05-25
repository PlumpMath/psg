''' Settings.py
	Author:			Chad Rempp
	Date:			2009/05/07
	Purpose:		The GameSettings class loads and saves global game
					settings. It also provides an interface for accessing
					settings.
	Usage:			None
	References:		None
	Restrictions:	None
	License:		TBD
	Notes:			The GameSettings object is a singleton.
'''

# Python imports
import re, sys, os.path

# PSG imports
from Util import Singleton

class GameSettings:
	''' This class provides storage for the game settings.
		This could be integrated into the Panda config file for'''
		
	__metaclass__=Singleton
	
	def __init__(self, cfgfile=None):
		''' Setup initial values.'''
		
		if cfgfile == None: self._cfgFilePath = 'data/config.cfg'
		else: self._cfgFilePath = self.cfgfile
		self._defaultDict = {
				'RESOLUTION': '800x600 ', 
				'FULLSCREEN': 'False',
				'SHOWFPS': 'True',
				'ALPHABITS': '16',
				'ANTIALIAS': '32',
				'COLORDEPTH': '16',
				'USEBLOOM': 'True', 
				'USEFOG': 'True'}
		self._configDict = None
		
	def getSetting(self, key):
		'''	Retrieve the value for the given key. If the key doesn't exist
			return None.'''
			
		if self._configDict.has_key(key):
			return self._configDict[key]
		else:
			return None
		
	def setSetting(self, key, value):
		self._configDict[key] = value
		
	def loadSettings(self):
		''' Load the configuration file and parse it filling in the _configDict.
			Modified from http://www.daniweb.com/forums/thread30215.html'''
			
		# Open File and read text
		if not(os.path.exists(self._cfgFilePath) or os.path.isfile(self._cfgFilePath)):
			self._configDict = self._defaultDict
			self.saveSettings()
		try: cfgFile = open(self._cfgFilePath, 'r')
		except Exception, e: raise
		try: cfgText = cfgFile.read()
		except Exception, e: raise
		
		# Put values int a dictionary. This regex kills the first line
		# so be sure the first line in the config file is a comment
		pattern = re.compile("\\n([\w_]+)[\t ]*([\w: \\\/~.-]+)")
		tuples = re.findall(pattern, cfgText)
		self._configDict = dict()
		for x in tuples: self._configDict[x[0]] = x[1]
		
		# Close file
		try: cfgFile.close()
		except Exception, e: raise
		
		# Check dict keys and fill in blanks with defaults
		if (self._configDict.keys() != self._defaultDict.keys()):
			for key in filter(lambda x: x not in self._configDict.keys(),self._defaultDict.keys()):
				self._configDict[key] = self._defaultDict[key]
				
		# Create some derivative values
		self._configDict['X_RES'] = int(self._configDict['RESOLUTION'].split()[0].split('x')[0])
		self._configDict['Y_RES'] = int(self._configDict['RESOLUTION'].split()[0].split('x')[1])
		
	def saveSettings(self):
		''' Save the current configuration state to the config file.'''
		
		# Open file
		try: cfgFile = open(self._cfgFilePath, 'w')
		except Exception, e: raise
		
		# Write title
		try: cfgFile.write("# Game Settings File\n")
		except Exception, e: raise
		
		# Write Settings
		for key in self._configDict.keys():
			try: cfgFile.write(key + "\t\t" + self._configDict[key] + "\n")
			except Exception, e: raise
		
		# Close file
		try: cfgFile.close()
		except Exception, e: raise
