import logging
import os


LOG_LEVEL = os.getenv('FYOO__LOG_LEVEL', default='info').upper()

logging.basicConfig(level=LOG_LEVEL)
