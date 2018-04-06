import logging
import logging.config
from os import path
import os


def get_logger():
    log_file = path.join(path.dirname(path.abspath(__file__)), 'loggger.conf')
    # logging.config.fileConfig(log_file, disable_existing_loggers=False)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger('root')
    logger.addHandler(handler)
    return logger
