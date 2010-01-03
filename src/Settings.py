''' Settings.py
	
	The GameSettings class loads and saves global game settings. It also provides
	an interface for accessing settings.
	
	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3
	Todo:			The GameSettings object is a singleton.
'''

# Python imports
import re, sys, os.path

# PSG imports
from Util.Singleton import Singleton

class GameSettings(object):
	''' This class provides storage for the game settings.
		This could be integrated into the Panda config file for'''
	
	__metaclass__ = Singleton
	
	def __init__(self, cfgfile=None):
		''' Setup initial values.'''
		
		LOG.notice("Creating game settings")
		
		self.resolution = '800x600'
		self.fullscreen = False
		self.showFPS    = True
		self.alphaBits  = 16
		self.antiAlias  = 16
		self.colorDepth = 16
		self.useBloom   = True
		self.useFog     = True
		
		if cfgfile == None: self._cfgFilePath = 'data/config.cfg'
		else: self._cfgFilePath = cfgfile
		
	def loadSettings(self):
		''' Load the configuration file and parse it filling in the _configDict.
			Modified from http://www.daniweb.com/forums/thread30215.html'''
		
		LOG.notice("Loading game settings")
		
		# If there is no config file save the defaults to a file.
		if not(os.path.exists(self._cfgFilePath) or os.path.isfile(self._cfgFilePath)):
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
		for x in tuples:
			if   x[0] == 'RESOLUTION':
				self.resolution = x[1]
			elif x[0] == 'FULLSCREEN':
				if x[1] == 'True':
					self.fullscreen = True
				else:
					self.fullscreen = False
			elif x[0] == 'SHOWFPS':
				if x[1] == 'True':
					self.showFPS = True
				else:
					self.showFPS = False
			elif x[0] == 'ALPHABITS':
				self.alphaBits = int(x[1])
			elif x[0] == 'ANTIALIAS':
				self.antiAlias = int(x[1])
			elif x[0] == 'COLORDEPTH':
				self.colorDepth = int(x[1])
			elif x[0] == 'USEBLOOM':
				if x[1] == 'True':
					self.useBloom = True
				else:
					self.useBloom = False
			elif x[0] == 'USEFOG':
				if x[1] == 'True':
					self.useFog = True
				else:
					self.useFog = False
			
		# Close file
		try: cfgFile.close()
		except Exception, e: raise
				
		# Create some derivative values
		self.xRes = int(self.resolution.split()[0].split('x')[0])
		self.yRes = int(self.resolution.split()[0].split('x')[1])
		
	def saveSettings(self):
		''' Save the current configuration state to the config file.'''
		
		LOG.notice("Saving game settings")
		
		# Open file
		try: cfgFile = open(self._cfgFilePath, 'w')
		except Exception, e:
			LOG.error("Could not open config file", e)
		
		# Write title
		try: cfgFile.write("# Game Settings File\n")
		except Exception, e:
			LOG.error("Could not write to config file", e)
		
		# Write Settings
		try:
			cfgFile.write("RESOLUTION\t\t" + self.resolution + "\n")
			cfgFile.write("FULSCREEN\t\t"  + self.fullscreen + "\n")
			cfgFile.write("SHOWFPS\t\t"    + self.showFPS + "\n")
			cfgFile.write("ALPHABITS\t\t"  + self.alphaBits + "\n")
			cfgFile.write("ANTIALIAS\t\t"  + self.antiAlias + "\n")
			cfgFile.write("COLORDEPTH\t\t" + self.colorDepth + "\n")
			cfgFile.write("USEBLOOM\t\t"   + self.useBloom + "\n")
			cfgFile.write("USEFOG\t\t"     + self.useFog + "\n")
		except Exception, e:
			LOG.error("Could not save settings to config file", e)
		
		# Close file
		try: cfgFile.close()
		except Exception, e:
			LOG.error("Could not close config file", e)
