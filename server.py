#!/usr/bin/python

import sys
import socket
import signal

import koshava

connection = None
sock = None

def quit(signum, frame):
    print >>sys.stderr, "Shutting down..."
    if connection:
        connection.close()
    sock.close()
    sys.exit(0)

signal.signal(signal.SIGINT, quit)




myKoschava = koshava.Koshava()

if not myKoschava.Connect():
    print "Could not connect to USB device!"
    sys.exit(1)

if not myKoschava.ProbeConnected():
    print "No hall probe connectetril d to device!"
    sys.exit()

myKoschava.ReadData()
myKoschava.SetAutorange(True)
myKoschava.SetAC(False)
myKoschava.SetRange(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_address = ('0.0.0.0', 1337)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

sock.listen(1)

def handleRequest(line):
    global myKoschava
    if( line == "read" ):
        B, mi, ma = myKoschava.ReadData()
        res = "read %0.5f %0.5f %0.5f" % (B, mi, ma)
    elif( line == "temp" ):
        res = "temp %0.1f" % myKoschava.GetTemp()
    elif( line == "quit" ):
        quit(0,0)
    else:
        res = "Unknown command: "+line

    return res+"\n"


def ActiveConnection(connection):
    # Receive the data in small chunks and retransmit it
    while True:
        data = connection.recv(16)
        if data:
            # print "<<", data
            response = handleRequest(data.strip())
            # print ">>", response
            connection.sendall(response)
        else:
            print >>sys.stderr, 'no more data from', client_address
            return


while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print >>sys.stderr, 'connection from', client_address
        ActiveConnection(connection)

        
    finally:
        # Clean up the connection
        connection.close()
