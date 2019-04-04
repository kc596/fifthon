from src.common.utils import *
from src.instagram.Instagram import Instagram

def test_config():
	config = loadConfiguration('config/config.yaml')
	assert len(config) > 0

