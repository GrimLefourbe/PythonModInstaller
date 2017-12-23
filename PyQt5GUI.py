import logging.config
import json

log = logging.getLogger(__name__)
logging.config.dictConfig(json.load(open('logging_config.json', 'r')))

if __name__ == '__main__':
    log.info('Starting GUI')