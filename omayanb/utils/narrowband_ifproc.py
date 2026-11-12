import os
import datetime
import logging
import time
import bisect

from .gpio_utils import NarrowBand
from omayanb.logging import logger

logger.name = __name__
address_mapper = {
    '17A': 0x90,
    '21A': 0x94,
    '25A': 0x98,
    '29A': 0x9C,
    '17B': 0xB0,
    '21B': 0xB4,
    '25B': 0xB8,
    '29B': 0xBC,
    }
    

class NarrowbandIFProcessor(object):
    def __init__(self, debug=True):
        self.debug = debug
        # logdir = os.path.join(os.path.expanduser('~'), 'logs')
        # logfile = os.path.join(logdir, datetime.datetime.now().strftime('omayanb_%Y_%m_%d_%H%M.log'))
        # logging.basicConfig(filename=logfile,
        #                     level=logging.INFO,
        #                     format='%(asctime)s %(levelname)s: %(message)s')
        self.atten_values = {'A':
                             {17:0, 18:0, 19:0, 20:0,
                              21:0, 22:0, 23:0, 24:0,
                              25:0, 26:0, 27:0, 28:0,
                              29:0, 30:0, 31:0, 32:0,
                              },
                             'B':
                             {17:0, 18:0, 19:0, 20:0,
                              21:0, 22:0, 23:0, 24:0,
                              25:0, 26:0, 27:0, 28:0,
                              29:0, 30:0, 31:0, 32:0,
                              },
                             }
        self.iflevels = {'A':
                         {17:0, 18:0, 19:0, 20:0,
                          21:0, 22:0, 23:0, 24:0,
                          25:0, 26:0, 27:0, 28:0,
                          29:0, 30:0, 31:0, 32:0,
                          },
                         'B':
                         {17:0, 18:0, 19:0, 20:0,
                          21:0, 22:0, 23:0, 24:0,
                          25:0, 26:0, 27:0, 28:0,
                          29:0, 30:0, 31:0, 32:0,
                          },
                         }        
        self.nb = NarrowBand()
        self.co = 0
        self.start_all()

    def _print(self, msg):
        if self.debug:
            print(msg)
        logger.info(msg)
        
    def start_all(self):
        self.set_init_attenuations(default=0, co=0)
        self.get_all_iflevels()
        
    def set_init_attenuations(self, default=0, co=0):
        self.co = co
        for bank in ('A', 'B'):
            for chan in range(17, 33):
                self.set_atten(bank, chan, default)
                time.sleep(0.01)

    def get_all_iflevels(self):
        for bank in ('A', 'B'):
            for chan in range(17, 33):
                level = self.get_level(bank, chan)
                self._print("IF Level for %d%s is %s" % (chan, bank, level))
        
    def get_base_chan(self, value):
        bchan = (17, 21, 25, 29)
        if value < 17:
            value = 17
            self._print("Channel should be between 17 to 32. Resetting to %d" % value)
        if value > 32:
            value = 32
            self._print("Channel should be between 17 to 32. Resetting to %d" % value)
        if value in bchan:
            return (value, 0)
        else:
            idx = bisect.bisect_left(bchan, value)
            return (bchan[idx-1], value - bchan[idx-1])

    def set_atten(self, bank, channel, value):
        if value < 0:
            value = 0
        if value > 31:
            value = 31
        bchan, chan = self.get_base_chan(channel)
        base_addr = address_mapper.get('%d%s' % (bchan, bank))
        self._print("set bank %s channel %s atten to %s" % (bank, channel, value))
        self.nb.write_byte(base_addr+chan, value|(self.co<<6))
        self.atten_values[bank][bchan + chan] = value

    def get_level(self, bank, channel):
        bchan, chan = self.get_base_chan(channel)
        base_addr = address_mapper.get('%d%s' % (bchan, bank))
        levels = self.nb.get_levels(base_addr)
        self.iflevels[bank][channel] = levels[chan]
        self._print("Getting level for  bank %s channel %s. Level: %s" % (bank, channel, levels[chan]))
        return levels[chan]

    def get_atten(self, bank, channel):
        self._print("Getting Atten for  bank %s channel %s. Atten: %s" % (bank, channel, self.atten_values[bank][channel]))
        return self.atten_values[bank][channel]

