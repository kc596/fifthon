import logging
import logging.config
import os
import yaml

configuration = ''

def loadConfiguration(configfile='config/config.yaml'):
	global configuration 					#needed to modify global copy of variable
	with open(configfile, 'r') as cf:
		config = yaml.safe_load(cf.read())
		configuration = config
	return config

def getLogger(name):
	createLogFileDirectory()
	logging.config.dictConfig(configuration['logs'])
	logger = logging.getLogger(name)
	return logger

def createLogFileDirectory():
	os.makedirs(os.path.dirname(str(configuration['logs']['handlers']['file']['filename'])), exist_ok=True)