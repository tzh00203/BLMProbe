import logging
import os

logging.basicConfig(filename=os.path.join(os.getcwd(),'log.txt'),level=logging.DEBUG)
logging.debug('debug message')
logging.info('info message')
logging.warning('warning message')
