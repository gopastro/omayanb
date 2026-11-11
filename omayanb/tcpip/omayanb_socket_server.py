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
from omayanb.logging import logger


#import SocketServer
logger.name = __name__

allowed_commands = ['set_atten', 'get_atten', 'get_level']

class OMAyANBSocketServer():
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

    def _print(self, msg):
        if self.debug:
            print(msg)
        logger.info(msg)    

    def listen(self, numconnections=10):
        self.sock.listen(numconnections)

    def accept(self):
        self.conn, self.addr = self.sock.accept()
        self._print("Connected by %s" % repr(self.addr))
        return True

    def recv(self, maxlen=1024):
        if self.conn:
            try:
                data = self.conn.recv(maxlen)
                return data
            except:
                self._print("No data")
                self.conn=None
                return None
        else:
            self._print("No connection")

    def process_omayanb_command(self):
        data = self.recv(1024)
        self.data = data.decode()
        if not self.data:
            return False
        else:
            msg = self.data.strip().split()
            if not msg:
                self.send("No command issued\n")
                self._print("No command sent")
                return True
            if not msg[0] in allowed_commands:
                logger.error("Request has to be one of %s" % allowed_commands)
                self.send("%s no_such_command\n" % self.data.strip())
                return True
            if msg[0] == 'get_atten':
                bank = msg[1]
                channel = int(msg[2])
                atten = self.nbif.get_atten(bank, channel)
                self.send("%s %s %s:  %s\n" % (msg[0], msg[1], msg[2], atten))

    def send(self, msg):
        if self.conn:
            self.conn.send(msg.encode()[:1024])

    def receive_with_size(self, msglen):
        msg = ''
        while len(msg) < msglen:
            chunk = self.sock.recv(msglen-len(msg))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            msg = msg + chunk
        return msg
    
    def close(self):
        self.sock.close()

    def conn_close(self):
        if self.conn:
            self.send('closed')
            self.conn.close()
            self._print("Connection to client closed")
