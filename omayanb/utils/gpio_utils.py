import os
import datetime
import logging
import time

import RPi.GPIO as GPIO


class NarrowBand(object):
    """
    A0-A7/D0-D7: Raspberry PI pins 4, 5, 6, 7, 8, 9, 10, 11
    D8-D15: Raspberry PI pins 12, 13, 14, 15, 16, 17, 18, 19
    R/W: 20
    A/S: 21
    D/S: 22
    """
    def __init__(self, debug=True):
        self.debug = debug
        logdir = os.path.join(os.path.expanduser('~'), 'logs')
        logfile = os.path.join(logdir, datetime.datetime.now().strftime('omayanb_%Y_%m_%d_%H%M.log'))
        logging.basicConfig(filename=logfile,
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s')
        self.pin_rw = 20           # Pin for R/W
        self.pin_as = 21           # Pin for Address Strobe
        self.pin_ds = 22           # Pin for Data Strobe
        self.address_pins = [4, 5, 6, 7, 8, 9, 10, 11]
        self.data_pins = [4, 5, 6, 7, 8, 9, 10, 11,
                          12, 13, 14, 15, 16, 17, 18, 19
                          ]
        # Set pin numbering mode
        GPIO.setmode(GPIO.BCM)
        self._print('Setting BCM Mode')
        for pin in (self.pin_rw, self.pin_as, self.pin_ds):
            GPIO.setup(pin, GPIO.OUT)
        self._print("Setting RW, AS, and DS pins to output pins")
        
    def _print(self, msg, loglevel=logging.INFO, ):
        if self.debug:
            print(msg)
        logging.log(level=loglevel, msg=msg)
    
    def write_adrs(self, addr):
        """
        Write specified address to IF Processor
        """
        # first setup the address pins as output pins
        for pin in self.address_pins:
            GPIO.setup(pin, GPIO.OUT)

        # set IF R/W to write
        GPIO.output(self.pin_rw, GPIO.LOW)
            
        bit_list = [(addr >> i) & 1 for i in range(8)]

        for (adr_pin, adr_val) in zip(self.address_pins, bit_list):
            GPIO.output(adr_pin, adr_val)

        self._print("Set address to %s" % addr)
        # generate address strobe
        GPIO.output(self.pin_as, GPIO.HIGH)
        GPIO.output(self.pin_as, GPIO.LOW)
        GPIO.output(self.pin_as, GPIO.HIGH)
        self._print("Generate Address strobe")
        
    def write_byte(self, addr, data):
        """
        Write byte to IF Processor.
        Write address first and then write
        data byte
        """
        self.write_adrs(addr)
        self._print("Wrote address : %s" % addr)
        # first setup the eight lowest data pins as output pins
        for pin in self.address_pins:
            GPIO.setup(pin, GPIO.OUT)        

        self._print("Writing data: %s" % data)
        data = data & 0xFF
        bit_list = [(data >> i) & 1 for i in range(8)]
        for (adr_pin, adr_val) in zip(self.address_pins, bit_list):
            GPIO.output(adr_pin, adr_val)

        # Generate data strobe
        GPIO.output(self.pin_ds, GPIO.HIGH)
        GPIO.output(self.pin_ds, GPIO.LOW)
        GPIO.output(self.pin_ds, GPIO.HIGH)
        self._print("Generated data strobe")
        # Set data inputs to input
        for pin in self.address_pins:
            GPIO.setup(pin, GPIO.IN)                
        # Set R/W to R
        GPIO.output(self.pin_rw, GPIO.HIGH)
    
    def read_byte(self, addr):
        """
        read byte from IF processor
        Write address and then read a byte
        """
        self.write_adrs(addr)

        # set A0/D0 through A7/D7 to input
        for pin in self.address_pins:
            GPIO.setup(pin, GPIO.IN)

        # Generate Data Strobe
        GPIO.output(self.pin_ds, GPIO.HIGH)
        GPIO.output(self.pin_ds, GPIO.LOW)

        # parallel read data pins
        byte_value = 0
        for pin in self.address_pins:
            byte_value = (byte_value << 1)|GPIO.input(pin)

        # reset data probe
        GPIO.output(self.pin_ds, GPIO.HIGH)
        return byte_value

    def read_lsbmsb(self, addr):
        """
        read lsbmsb (short) from if processor.  write address, then read
        data lsb, data msb from if processor
        """
        self.write_adrs(addr)

        # configure all data bits as inputs
        for pin in self.data_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # set IF R/W to read
        GPIO.output(self.pin_rw, GPIO.HIGH)

        # generate data strobe
        GPIO.output(self.pin_ds, GPIO.HIGH)
        GPIO.output(self.pin_ds, GPIO.LOW)
        time.sleep(0.005)

        # parallel read data pins
        lsb_value = 0
        for pin in self.address_pins:
            lsb_value = (lsb_value << 1)|GPIO.input(pin)

        msb_value = 0
        for pin in self.data_pins[8:]:
            msb_value = (msb_value << 1)|GPIO.input(pin)
        self._print("LSB: 0x%x; MSB: 0x%x" % (lsb_value, msb_value))
        #reset data strobe
        GPIO.output(self.pin_ds, GPIO.HIGH)

        return (msb_value << 8) | lsb_value
        #return (lsb_value << 8) | msb_value

    def read_short(self, addr):
        """
        wrapper for read_lsbmsb
        """
        return self.read_lsbmsb(addr)

    def get_levels(self, base_addr):
        """
        Given a card's base address get 
        channel (0 - 3) within it, read and get levels
        """
        levels = []
        for channel in range(4):
            # Do a start conversion for every 4th read
            if not (channel % 4):
                data = self.read_short(base_addr)
                self._print("SOC done: data: %s" % data)
        
            # Read 4 voltages from base_addr + 1
            adrs = base_addr + 1
            data = 0
            for trycnt in range(5):
                data = self.read_short(adrs)
                #data = data & ~0x8000  # clear 16th bit
                if not (data & 0x8000):
                    data = data & 0x0FFF
                    data += 2048
                    data = data % 4096
                    break
            self._print("Data: %s, trycnt: %d" % (data, trycnt))
            levels.append((data/4096.0) * 10.0)
            time.sleep(0.01)
        return levels
                
        
    

    
