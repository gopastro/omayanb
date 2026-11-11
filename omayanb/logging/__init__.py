"""
Logging Framework for OMAyA Narrowband IF Processor
TODO: Simple test cases
"""

import logging as pylogging
import logging.handlers as handlers
import os
import datetime

DEBUG0 = 5
DEBUG1 = 6
DEBUG2 = 7
DEBUG3 = 8
DEBUG4 = 9
DEBUG  = 10
INFO   = 20
WARNING = 30
ERROR  = 40
CRITICAL = 50

def _get_omayanb_logname():
    """
    Returns the path to the omayanb log file
    """
    homedir = os.path.expanduser('~')
    if os.path.exists(homedir):
        if os.path.exists(os.path.join(homedir, 'logs')):
            fname = os.path.join(homedir, 'logs', datetime.datetime.now().strftime('omayanb_%Y_%m_%d_%H%M.log'))
        else:
            fname = os.path.join(homedir, datetime.datetime.now().strftime('omayanb_%Y_%m_%d_%H%M.log'))
        return fname
    else:
        return datetime.datetime.now().strftime('omayanb_%Y_%m_%d_%H%M.log')


class NullHandler(pylogging.Handler):
    """A simple NullHandler to be used by modules used
    inside omayanb
    Every module can use at least this one null handler.
    It does not do anything. The application that uses the
    omayanb library can set up logging, and setup appropriate
    handlers, and then the omayanb library will appropriately
    handle correct logging.
    A omayanb module should do the following:
    from omayanb.logging import logger
    logger.name = __name__  #to appropriately catch that module's logs
    And then you can use the logger object within the modules
    """
    def emit(self, record):
        pass

def will_debug():
    return logger.isEnabledFor(pylogging.DEBUG)

def add_file_handler(log, fname):
    handler = handlers.RotatingFileHandler(fname, maxBytes=1000000,
                                           backupCount=1)
    #handler = pylogging.FileHandler(fname)
    # create formatter
    formatter = pylogging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #level = omayanbParams['omayanb'].get('loglevel', 10)
    #handler.setLevel(level)
    handler.setLevel(pylogging.DEBUG)
    handler.setFormatter(formatter)
    #print "Setting up Rotating File Handler %s" % fname
    log.addHandler(handler)

def add_stream_handler(log):
    handler = pylogging.StreamHandler()
    #level = omayanbParams['omayanb'].get('loglevel', 10)
    handler.setLevel(pylogging.DEBUG)
    #handler.setLevel(level)
    log.addHandler(handler)

def debug_factory(logger, debug_level):
    def custom_debug(msg, *args, **kwargs):
        if logger.level >= debug_level:
           return
        logger._log(debug_level, msg, args, kwargs)
    return custom_debug    


logger = pylogging.getLogger('omayanb')
logger.logging = pylogging
logger.addHandler(NullHandler())
logger.will_debug = will_debug
add_file_handler(logger, _get_omayanb_logname())
add_stream_handler(logger)
logger.setLevel(DEBUG0)

for i in range(5, 10):
    pylogging.addLevelName(i, 'DEBUG%i' % (i-5))
    setattr(logger, 'debug%i' % (i-5), debug_factory(logger, i))
