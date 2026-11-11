#!/usr/bin/python
"""
A class for receiving OMAyANB (OMAyA Narrowband) IF Processor
monitor and control commands
via TCP/IP sockets
"""

import socket
import sys
import traceback
import time
#import logging
from msipbias.logging import logger
from msipbias.msipwrapper import MSIPWrapper

import SocketServer
logger.name = __name__

allowed_commands = ['set_atten', 'get_atten', 'get_level']

class MSIP1mmSocketServer():
    debug = 0
    status_bytes = []
    status_dict = {}
