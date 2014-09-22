#!/usr/bin/python

import sys
import time
import signal

import koshava

def quit(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, quit)

print "a"

myKoschava = koshava.Koshava()

print "b"
if not myKoschava.Connect():
    print "Could not connect to USB device!"
    sys.exit(1)

if not myKoschava.ProbeConnected():
    print "No hall probe connectetril d to device!"
    sys.exit()

while(True):

    line = raw_input(">")

    if( line ):
        if( line == "r" ):
            B, mi, ma = myKoschava.ReadData()
            print "r %0.5f, %0.5f, %0.5f" % (B, mi, ma)
        elif( line == "temp" ):
            print "temp %0.1f" % myKoschava.GetTemp()
        else:
            print line, len(line)

