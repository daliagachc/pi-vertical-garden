# project name: pi-vertical-garden
# created by diego aliaga daliaga_at_chacaltaya.edu.bo
import logging

logger = logging.getLogger('pvg')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)
