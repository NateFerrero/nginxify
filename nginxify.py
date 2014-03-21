#!env python
import json
import glob

master = {}

for path in glob.glob('/home/*/.nginx'):
	with open(path) as file:
		conf = json.load(file)
		print conf
