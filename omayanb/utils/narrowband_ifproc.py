import os
import datetime
import logging
import time

from .gpio_utils import NarrowBand

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
        logdir = os.path.join(os.path.expanduser('~'), 'logs')
        logfile = os.path.join(logdir, datetime.datetime.now().strftime('omayanb_%Y_%m_%d_%H%M.log'))
        logging.basicConfig(filename=logfile,
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s')
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
        self.nb = NarrowBand()
        self.start_all()

    def start_all(self):
        self.set_init_attenuations(default=0, co=0)

    def set_init_attenuations(self, default=0, co=0):
        self.co = co
        for bank in ('A', 'B'):
            for bchan in range(17, 33, 4):
                base_addr = address_mapper.get('%d%s' % (bchan, bank))
                for chan in range(4):
                    nb.write_byte(base_addr+chan, default|(co<<6))
                    self.atten_values[bank][bchan+chan] = default
                    time.sleep(0.01)

                
                        
    '
