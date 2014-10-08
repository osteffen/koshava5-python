#!/usr/bin/python

import sys
import time
import signal

import koshava

def quit(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, quit)

myKoschava = koshava.Koshava()

if not myKoschava.Connect():
    print "Could not connect to USB device!"
    sys.exit(1)

if not myKoschava.ProbeConnected():
    print "No hall probe connected to device!"
    sys.exit(2)

myKoschava.ReadData()
myKoschava.SetAutorange(True)
myKoschava.SetAC(False)

myKoschava.SetRange(1)

while(True):
    B, mi, ma = myKoschava.ReadData()

    print "%0.5f, %0.5f, %0.5f, %d" % (B, mi, ma, myKoschava.GetRange())

    time.sleep (.5)


