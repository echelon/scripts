#!/usr/bin/env python
# Script Installation and Management Script
# Copyright 2009 Brandon Thomas Suit

import os
import os.path
import subprocess
import sys

INSTALL_PATH = './installed'

# TODO: Replace with config/xml/ini file.
VALID_SCRIPTS = {
	'resize-fonts': './source/gnome/resize-fonts.py'
}

def installScript(name):
	"""Install the script corresponding to the key."""
	if name not in VALID_SCRIPTS:
		return False
	exePath = os.path.abspath(VALID_SCRIPTS[name])
	installPath = os.path.abspath(INSTALL_PATH)
	lnPath = installPath + '/' + name

	chmod = "chmod +x %s" % exePath
	print chmod
	subprocess.Popen(chmod, shell=True, executable='/bin/bash')

	link = "ln -s %s %s" % (exePath, lnPath)
	print link
	subprocess.Popen(link, shell=True, executable='/bin/bash')

# TODO
def uninstallScript(name):
	pass

def getPath():
	"""Simply get what the $PATH variable should be with the install path."""
	paths = os.environ['PATH'].split(':')
	abspath = os.path.abspath(INSTALL_PATH)
	if abspath in paths:
		return ":".join(paths)
	paths.append(abspath)
	return ":".join(paths)

def ensureInstallPath():
	"""Insure that the script install path is set in the $PATH environment.
	variable. If it's not there, ask the system to permanently store it."""
	paths = os.environ['PATH'].split(':')
	abspath = os.path.abspath(INSTALL_PATH)
	if abspath in paths:
		return -1

	rcFile = os.path.expanduser("~/.bashrc")
	fh = open(rcFile, 'r')
	rcContents = fh.read()
	fh.close()

	# This won't work on Unix...
	paths.append(abspath)
	os.environ['PATH'] = ":".join(paths)

	# A total of 3 new lines will be installed into bashrc.
	s1 = "# PYTHON SCRIPT INSTALLED [BT] (ver 1.0)"
	s2 = "# PYINSTALLED"
	line = "\n%s\nPATH=$PATH:%s %s\n" % (s1, abspath, s2)

	if s1 in rcContents:
		print "Already installed in '%s'" % rcFile
		return True

	fh = open(rcFile, 'a')
	fh.write(line)
	fh.close()

	print "Successfully installed in '%s'" %rcFile
	return True

def main():
	ret = ensureInstallPath()
	if ret and ret != -1:
		print "\nNote that $PATH installation doesn't take effect " +\
				"in already open shells!"

if __name__ == '__main__':
	main()
	installScript('resize-fonts')
