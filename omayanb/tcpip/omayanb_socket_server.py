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
from omayanb.utils.narrowband_ifproc import NarrowbandIFProcessor


#import SocketServer
logger.name = __name__

allowed_commands = ['set_atten', 'get_atten', 'get_level']

class MSIP1mmSocketServer():
    debug = 0
    status_bytes = []
    status_dict = {}
    
    def __init__(self, HOST='0.0.0.0', PORT=None):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if HOST:
                self.sock.bind((HOST, PORT))
            else:
                self.sock.bind((socket.gethostname(), PORT))
            self.conn = None
            self.addr = None
            #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.nbif = NarrowbandIFProcessor(debug=True)
        except:
            logger.error(str(self.formatExceptionInfo()))

    def formatExceptionInfo(self, maxTBlevel=5):
        """copied from Linux Journal article 5821"""
        cla, exc, trbk = sys.exc_info()
        excName = cla.__name__
        try:
            excArgs = exc.__dict__["args"]
        except KeyError:
            excArgs = "<no args>"
        excTb = traceback.format_tb(trbk, maxTBlevel)
        return (excName, excArgs, excTb)
