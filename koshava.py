#!/usr/bin/python

import usb.core
import sys
import pdb
import array
import time


class Koshava:
    VENDOR_ID = 0x21c5
    PRODUCT_ID = 0x03e8
    device = None
    ep_in = None
    ep_out = None
    units = ['T','G','V/cm','KV/m','Oe' ]

    def isConnected(self):
        return (self.device is not None and self.ep_in is not None and self.ep_out is not None)

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
        else:
            print "Endpoint OUT found @", self.ep_out.bEndpointAddress

        self.ep_in = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)

        if self.ep_in is None:
           raise ValueError('Endpoint IN not found') 
        else:
            print "Endpoint IN found @", self.ep_in.bEndpointAddress

        return True

    def write(self, msg):
        #print "Write:", msg
        try:
            self.ep_out.write(msg)
        except usb.core.USBError,e:
            print e
            pass

    def read(self):
        try:
            m = self.ep_in.read(64)
            #print "Read:",m
            return m
        except usb.core.USBError, e:
            print e
            return None

    def makeMessage(self, cmd):
        msg = bytearray(64)
        msg[0] = chr(cmd)
        return msg

    def bytes2short(self, bts):
        return bts[1]*256+bts[0]

    def handle1D(self, msg):
        adc_ = msg[2:4]
        adc = self.bytes2short(adc_)
        rangepos = msg[4]
        unit = msg[5]
        acdc = msg[6]
        autorange = (msg[13] == 1)
        temp_ = msg[14:16]
        temp = self.bytes2short(temp_)/10.0

        print "Unit: ", unit, self.units[unit]
        print "AC/DC:" , acdc
        print "adc:",adc
        print "autorange:",autorange
        print "Temp:",temp


    def handle32(self, msg):
        probe_connected = (msg[1] == 1)
        print "Probe is connected?", probe_connected

    def handleC1(self,msg):
        name = msg[2:22]
        print name

    def handleALL(self, msg):
        cmd = msg[0]
        print cmd

        if(cmd == 0x1D):
            self.handle1D(msg)
        elif(cmd == 0x32):
            self.handle32(msg)
        elif(cmd == 0xc1):
            self.handleC1(msg)

    def sendcmd(self, cmd):
        msg = self.makeMessage(cmd)
        self.write(msg)
        reply = self.read()

        if( reply is not None ):
            self.handleALL(reply)
        else:
            print "No reply!"


myKoschava = Koshava()

myKoschava.Connect()

myKoschava.sendcmd(0xC1)
myKoschava.sendcmd(0x32)

while(True):
    myKoschava.sendcmd(0x1D)
    time.sleep (.5)
