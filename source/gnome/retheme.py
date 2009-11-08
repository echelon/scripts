#!/usr/bin/env python
# Brandon Thomas
# @web <http://possibilistic.org>
# @email <brandon.suit@gmail.com>

##
# GConf retheme script
#
# Copyright : (C) 2008 Brandon Thomas
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

## Retheme ##########
# This script can be used to specify a set of themes for any attribute 
# of the Gnome environment one wishes to change. Together, one can 
# collect these into "themes" and cycle through them. 

import gconf

#from xml import xpath
import libxml2
from xml.dom.minidom import parse
from xml.dom.minicompat import NodeList

from pprint import *

class ThemeTool:

	def __init__(self, filename):
		"""Read the XML configuration file"""

		tree = parse(filename)
		root = tree.getElementsByTagName("retheme")[0]

		tree2 = libxml2.parseFile(filename)

		# TODO: The XQuery/DOM bit could be cleaned up a lot.

		# keys[name] -> ["key":/path/to/key, "type":list|None]
		keys = {}
		found = tree2.xpathEval('/retheme/keys/key')

		for k in found:
			name  = ""
			key   = ""
			ktype = None

			for attr in k.get_properties():
				k = attr.name
				v = attr.children

				if not v:
					continue
				if k == 'name':
					name = str(v)
				elif k == 'var':
					key = str(v)
				elif k == 'type':
					ktype = str(v)

			keys[name] = {'key': key, 'type': ktype}

		# themes[0] -> [{key1:val, key2:val}]
		themes = []
		found = tree2.xpathEval('/retheme/themes/theme')
		for t in found:
			if not t.children:
				continue

			curtheme = {}
			sets = t.xpathEval('set')
			for s in sets:
				chk = str(s.properties.name)
				key = str(s.properties.children)
				val = str(s.children)
				if chk != 'key': 
					continue
				curtheme[key] = val
			if curtheme:
				themes.append(curtheme)

		self.keys = keys
		self.themes = themes
		self.gclient = gconf.client_get_default()

	def keyExists(self, keyname):
		"""See if the key exists"""
		return (keyname in self.keys)

	def getKeyType(self, keyname):
		"""Get the key value"""
		if not self.keyExists(keyname):
			return False
		return self.keys[keyname]['type']

	def getKeyPath(self, keyname):
		"""Get the key value"""
		if not self.keyExists(keyname):
			return False
		return str(self.keys[keyname]['key'])

	def getCurrentTheme(self):
		"""Guesses the current theme based on first perfect match to theme"""
		for i in range(len(self.themes)):
			theme = self.themes[i]
			isTheme = True
			for (key, val) in theme.items():
				if not self.keyExists(key):
					isTheme = False

				kname = self.getKeyPath(key)
				ktype = self.getKeyType(key)

				chkval = None
				if ktype == 'list':
					chkval = self.gclient.get_list(kname, gconf.VALUE_STRING)[0]
				else:
					chkval = self.gclient.get_value(kname)
					if ktype == 'int':
						val    = int(val)
					elif ktype == 'float':
						val    = float(val)

				if chkval != val:
					isTheme = False

			if isTheme:
				return i
		return False

	def invokeTheme(self, offset):
		"""Set the theme that's at the specified offset
		If index is invalid, use index 0."""
		if offset >= len(self.themes) or offset < 0:
			offset = 0

		# Set each key to its value
		for themeset in self.themes[offset].items():
			k = themeset[0]
			value = str(themeset[1])
			if not self.keyExists(k):
				continue

			key = self.getKeyPath(k)
			ktype = self.getKeyType(k)

			if ktype == 'list':
				self.gclient.set_list(key, gconf.VALUE_STRING, [value])
			elif ktype == 'int':
				self.gclient.set_value(key, int(value))
			elif ktype == 'float':
				self.gclient.set_value(key, float(value))
			else:
				self.gclient.set_value(key, value)

	def iterateTheme(self):
		"""Iterate to the next theme"""
		theme = self.getCurrentTheme()
		if type(theme) == bool:
			theme = 0
		else:
			theme+=1
		self.invokeTheme(theme)

def main():
	"""Main func.
	Here we toggle the values.
	"""

	import sys, os
	#for i in range(10):
	#	change_skydome()
	#	time.sleep(7)

	#setup()

	t = ThemeTool("./.retheme.xml")

	t.iterateTheme()

if __name__ == '__main__': main()
