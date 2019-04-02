from src.common.utils import *
from src.instagram.Instagram import Instagram

config = loadConfiguration('config/config.yaml')
credentials = loadCredentials('config/credentials.yaml')
logger = getLogger(__name__)
logger.info("Initializing Instagram crawler, handle: "+credentials['instagram']['user'])
instagram = Instagram(credentials['instagram'], credentials['instagram']['user'])
logger.info("Instagram crawling completed for handle: "+credentials['instagram']['user'])