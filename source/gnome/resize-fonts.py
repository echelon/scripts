#!/usr/bin/env python2.6
# Resize the Gnome system fonts
# This is good for TV-based monitors. Use to easily switch between sitting up
# close and moving far away. 
# (I know the code is a little verbose, but it should be easily adaptable to 
# other gconf-setting code.)
# Copyright 2009 Brandon Thomas Suit, released under LGPL 2
# @web http://possibilistic.org
# @email echelon@gmail.com

##
# Gnome Resize Fonts Script
#
# Copyright : (C) 2009 Brandon Thomas Suit
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
##

import gconf
import libxml2
import os.path

class Font(object):
	"""Represents a single font setting for a single GConf key."""
	def __init__(self, face=None, size=None):
		"""Font CTOR. Can supply a face and size, or a string combining both. 
		Face is the 'name' of the font, eg. Arial. 
		Size is the point value."""
		self.face = None
		self.size = None

		if size:
			self.face = face
			self.size = size
		else:
			(face, sep, size) = face.rpartition(" ")
			self.face = face
			self.size = int(size)

	def getName(self):
		"""Return the font name in GConf spec."""
		return "%s %d" % (self.face, self.size)

	def __str__(self):
		return "<Font: %s %d>" % (self.face, self.size)


class Config(object):
	"""Represents a set of zero or more key-value configurations."""
	def __init__(self, key, description, assign = None):
		self.key = key
		self.description = description
		self.assign = {}
		if type(assign) == dict:
			self.assign = assign

	def set(self, key, val):
		"""Set a single assignment parameter."""
		if not key or not val or val == 'None':
			return False
		self.assign[key] = val

	def __len__(self):
		"""The number of assignments"""
		return len(self.assign)

	def __str__(self):
		ret = "<Config %s \"%s\"" % (self.key, self.description)
		for x in self.assign.items():
			ret += "\n    %s=%s" % x
		ret += ">"
		return ret

	def __repr__(self):
		return "<Config \"%s\">" % self.description


def parseXmlConfig(filename):
	"""Parse the XML config file and return Config objects for each set found"""
	xmlDoc = libxml2.parseFile(filename)
	modes = xmlDoc.xpathEval('/fonts/modes/mode')
	if not modes:
		return False

	configs = []
	for x in modes:
		config = None
		try:
			key =  str(x.xpathEval('./@key')[0].lastChild())
			comment = str(x.xpathEval('./@comment')[0].lastChild())
			config = Config(key, comment)
		except:
			continue

		for y in x.children:
			key = str(y.name)
			val = str(y.children)
			config.set(key, val)
		configs.append(config)

	return configs


class GnomeFonts(object):
	"""Represents the GNOME GConf environment and a few font-related keys that 
	we can change."""
	KEYS = {
		# GNOME
		'default' : '/desktop/gnome/interface/font_name',
		'document': '/desktop/gnome/interface/document_font_name',
		'monospace': '/desktop/gnome/interface/monospace_font_name', 

		# Applications
		'avant': '/apps/avant-window-navigator/title/font_face',
		'gedit': '/apps/gedit-2/preferences/editor/font/editor_font',
		'nautilus-desktop': '/apps/nautilus/preferences/desktop_font',

		# Window Manager
		'metacity': '/apps/metacity/general/titlebar_font'
	}

	def __init__(self):
		"""CTOR."""
		self.conf = gconf.client_get_default()

	def getFont(self, key):
		"""Get the font for the corresponding key."""
		cls = self.__class__
		if key not in cls.KEYS:
			return False
		#if not self.conf.dir_exists(cls.KEYS[key]):
		#	return False
		fName = self.conf.get_string(cls.KEYS[key])
		return Font(fName)

	def setFont(self, key, font):
		"""Set the font for the corresponding key."""
		if not font:
			return False
		if not font.face:
			self.setFontSize(key, font.size)
			return
		cls = self.__class__
		self.conf.set_string(cls.KEYS[key], font.getName())

	def setFontSize(self, key, size):
		"""Set the font size for the corresponding key."""
		cls = self.__class__
		if type(size) != int:
			return False
		font = self.getFont(key)
		if not font:
			return False
		font.size = size
		self.conf.set_string(cls.KEYS[key], font.getName())

	def setConfig(self, config):
		if not config:
			return False

		for x in config.assign.items():
			key = x[0]
			font = Font(x[1])
			self.setFont(key, font)

	def checkCurrent(self, configSet):
		"""Finds which is the current config (in a list of configs), or None."""
		match = None
		for config in configSet:
			found = True
			for a in config.assign.items():
				new = Font(a[1])
				cur = self.getFont(a[0])
				if new.size != cur.size:
					found = False
					break
			if found:
				match = config.key
				break
		return match

	def toggleSetting(self, configSet):
		"""Set the fonts to the next non-matching config."""
		if len(configSet) < 2:
			return False
		setConfig = None
		curKey = self.checkCurrent(configSet)
		curConfigIdx = None
		if not curKey:
			setConfig = configSet[0]
		else:
			for i in range(len(configSet)):
				config = configSet[i]
				if curKey == config.key:
					curConfigIdx = i
					break

		if type(curConfigIdx) != int:
			setConfig = configSet[0]
		else:
			setConfig = configSet[(curConfigIdx+1) % len(configSet)]

		self.setConfig(setConfig)

		for config in configSet:
			if setConfig.key == config.key:
				print "* %s" % repr(config)
			else:
				print "  %s" % repr(config)

def main():
	gnomeFonts = GnomeFonts()
	dirname = os.path.dirname(os.path.realpath(__file__))
	configs = parseXmlConfig(os.path.abspath(dirname+'/resize-fonts.xml')) #TODO
	gnomeFonts.toggleSetting(configs)

if __name__ == '__main__': main()

