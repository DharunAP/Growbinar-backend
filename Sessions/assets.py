import logging
import inspect


def log(message,code):
    logger = logging.getLogger("Sessions")
    # this inspect.stack provides the funcion name which called this log
    message = str(inspect.stack()[1][3])+" message - "+message
    if code==1:
        logger.debug(message)
    elif code==2:
        logger.warn(message)
    elif code==3:
        logger.error(message)
