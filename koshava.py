#!/usr/bin/python

import usb.core
import sys
import pdb

VENDOR_ID = 0x21c5
PRODUCT_ID = 0x03e8

device = usb.core.find(idVendor=VENDOR_ID,
                       idProduct=PRODUCT_ID)

if device is None:
   raise ValueError('Device not found')
else:
    print "Found the probe! (",'{0:04x}'.format(VENDOR_ID),"-",'{0:04x}'.format(PRODUCT_ID),")"


device.set_configuration()

cfg = device.get_active_configuration()

intf = cfg[(0,0)]

if device.is_kernel_driver_active(intf):
    print "Kernel Driver is active"
    if device.detach_kernel_driver(intf):
        print "Detached kernel driver"
    else:
        print "Unable to detach kernel driver"
        sys.exit(1)
else:
    print "Kernel driver is inactive. Good!"



## Probing for end points
ep_out = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

if ep_out is None:
   raise ValueError('Endpoint OUT not found') 
else:
    print "Endpoint OUT found @", ep_out.bEndpointAddress
    print ep_out.bmAttributes

ep_in = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN)

if ep_in is None:
   raise ValueError('Endpoint IN not found') 
else:
    print "Endpoint IN found @", ep_in.bEndpointAddress
    print ep_in.bmAttributes

#pdb.set_trace()
## read
m = ep_in.read(64)
# device.read() does the same

print m
