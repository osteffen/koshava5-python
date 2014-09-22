#!/usr/bin/python

import usb.core
import sys
import pdb
import array
import time
import struct

class Koshava:

    # USB IDs of the Koshava 5
    VENDOR_ID = 0x21c5
    PRODUCT_ID = 0x03e8

    # USB connection __handlers
    device = None
    ep_in = None
    ep_out = None

    # static data
    units = ['T', 'G', 'V/cm', 'KV/m', 'Oe' ]   # Unit names
    convT = [ 1.0, 1.0/10 ,1.0/(10*1000), 1.0/(100*1000), 1.0 ] # Conversion factors to Tesla for each range
    rangetxt = [ 'Invalid', '2T', '200mT', '20mT', 'Invalid' ]  # Range names

    # Probe state values
    probeConnected = False
    rangepos = 0
    adc = 0
    unit = 0
    acdc = 0
    autorange = False
    temp = 0
    B = 0
    minB = 0
    maxB = 0

    """Check if the USB connection is established"""
    def isConnected(self):
        return (self.device is not None and self.ep_in is not None and self.ep_out is not None)

    """Connect to the device"""
    def Connect(self):
        
        self.device = usb.core.find(idVendor=self.VENDOR_ID,
                       idProduct=self.PRODUCT_ID)

        if self.device is None:
           raise ValueError('Device not found')
        else:
            print "Found the probe! (",'{0:04x}'.format(self.VENDOR_ID),"-",'{0:04x}'.format(self.PRODUCT_ID),")"


        self.device.set_configuration()

        cfg = self.device.get_active_configuration()

        intf = cfg[(0,0)]

        if self.device.is_kernel_driver_active(intf):
            print "Kernel Driver is active"
            if device.detach_kernel_driver(intf):
                print "Detached kernel driver"
            else:
                print "Unable to detach kernel driver"
                sys.exit(1)
        else:
            print "Kernel driver is inactive. Good!"



        ## Probing for end points
        self.ep_out = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

        if self.ep_out is None:
           raise ValueError('Endpoint OUT not found') 
       #else:
       #     print "Endpoint OUT found @", self.ep_out.bEndpointAddress

        self.ep_in = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)

        if self.ep_in is None:
           raise ValueError('Endpoint IN not found') 
       #else:
        #    print "Endpoint IN found @", self.ep_in.bEndpointAddress

        # confiure probe with default settings
        self.setValues()

        return True

    """Write a binary message to the probe"""
    def __write(self, msg):
        try:
            self.ep_out.write(msg)
        except usb.core.USBError,e:
            print "WRITE:", e
            pass

    """Read from the device"""
    def __read(self):
        try:
            m = self.ep_in.read(64)
            return m
        except usb.core.USBError, e:
            print "READ:", e
            return None

    def __makeMessage(self, cmd):
        msg = bytearray(64)
        msg[0] = chr(cmd)
        return msg

    def __bytes2short(self, bts):
        return struct.unpack('h', self.__array2string(bts))[0]

    def __handle1D(self, msg):
        self.adc = self.__bytes2short(msg[2:4])
        self.rangepos = msg[4]
        self.unit = msg[5]
        self.acdc = msg[6]
        self.autorange = (msg[13] == 1)
        self.temp = self.__bytes2short(msg[14:16]) / 10.0
        self.minB = self.__bytes2short(msg[ 9:11]) * self.convT[self.rangepos]
        self.maxB = self.__bytes2short(msg[11:13]) * self.convT[self.rangepos]
        self.B = self.adc * self.convT[ self.rangepos ]

    def __handle32(self, msg):
        self.probeConnected = (msg[1] == 1)

    def __array2string(self, arr):
        s = "".join(chr(b) for b in arr) 
        return s

    def __handle1C(self,msg):
        self.devicename = self.__array2string(msg[2:22])
        self.deviceno = msg[22:31]
        self.probename = self.__array2string(msg[31:53])
        self.probecalibdate= msg[53:57]
        self.probeno = msg[57:62]

    def __handleALL(self, msg):
        cmd = msg[0]

        if(cmd == 0x1D):
            self.__handle1D(msg)
        elif(cmd == 0x32):
            self.__handle32(msg)
        elif(cmd == 0x1c):
            self.__handle1C(msg)
        elif(cmd == 0x2a):
            self.__handle2a(msg)

    def __sendcmd(self, cmd, answer=True):
        msg = self.__makeMessage(cmd)
        self.__write(msg)

        if( answer ):
            reply = self.__read()
            if( reply is not None ):
                self.__handleALL(reply)
            else:
                print "No reply!"

    def setValues(self, vrange=3, unit=0, acdc=0, lang=0, autorange=False):
        msg = self.__makeMessage(0x2a)
        msg[1] = chr(0x2a)
        msg[4] = chr(vrange)
        msg[5] = chr(unit)
        msg[6] = chr(acdc)
        msg[7] = chr(lang)
        msg[13] = chr( 1 if autorange else 0 )
        self.__write(msg)

        reply = self.__read()
        if( reply is not None ):
            self.__handleALL(reply)
        else:
            print "No reply!"


    def __handle2a(self, msg):
        print msg


    """Set auto-ranging. returns True if on, False if off"""
    def SetAutorange(self, state=True):
        self.setValues(vrange=self.rangepos, unit=self.unit, acdc=self.acdc, lang=0, autorange=True)
        return self.autorange

    """Check if auto-ranging is on (True) or off (False)"""
    def GetAutorange(self):
        return self.autorange

    """Set the measuring range (1..4)"""
    def SetRange(self, r=0):
        self.setValues(vrange=r, unit=self.unit, acdc=self.acdc, lang=0, autorange=self.autorange)
        return self.rangepos

    """Get the current measuring range as number (1..4)"""
    def GetRange(self):
        return self.rangepos

    """Get the current measuring range as text name (e.g. 20mT)"""
    def GetRangeTxt(self):
        return self.rangetxt[self.rangepos]

    """Set measuring mode to AC. Returns True on success"""
    def SetAC(self, ac=True):
        self.setValues(vrange=self.rangepos, unit=self.unit, acdc=ac, lang=0, autorange=self.autorange)
        return self.acdc

    """Check if measureing mode is AC (True) or DC (False)"""
    def GetAC(self):
        return self.acdc

    """Get the probe name"""
    def GetProbeName(self):
        return self.probename

    """Get the device name"""
    def GetDeviceName(self):
        return self.devicename

    """Read data from the device. Returns (B, B_min, B_max)"""
    def ReadData(self):
        self.__sendcmd(0x1d)
        return self.B, self.minB, self.maxB

    """Check if a hall probe is connected to the device"""
    def ProbeConnected(self):
        self.__sendcmd(0x32)
        return self.probeConnected

    """Get measured field in Tesla"""
    def GetB(self):
        return self.B

    """Get probe temperature in Celsius"""
    def GetTemp(self):
        return self.temp


myKoschava = Koshava()

if not myKoschava.Connect():
    print "Could not connect to USB device!"
    sys.exit(1)

if not myKoschava.ProbeConnected():
    print "No hall probe connected to device!"
    sys.exit(2)

while(True):
    B, mi, ma = myKoschava.ReadData()

    print "%0.5f, %0.5f, %0.5f" % (B, mi, ma)

    time.sleep (.5)

#myKoschava.setValues(unit=0, vrange=3, autorange=True)
#myKoschava.sendcmd(0x1D)
#time.sleep (.5)
