#! /usr/bin/python2
# Author: Nate Ferrero

import json
import glob

master = {}

for path in glob.glob('/home/*/.nginx'):
	with open(path) as file:
		conf = json.load(file)
		print conf
