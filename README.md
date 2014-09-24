# koshava5-python


Read the Koshava5 Hall Probe with Python.
Uses pyUSB for USB communication and partially implements the protocol to talk to the probe.
It can read magetic field values and the probe temperature, set configuration options such as range, AD/DC, and autorange.
Allows you to use your Koshava5 hall probe with a Raspberry Pi.

Currently only tested under Linux but should be easy to port to other platforms.
Since I only have a probe with three measuring ranges only these are implemented right now. Feel free to contribute!


## The Koshava5 and Linux

Some magic is required to get the probe working under Linux.
The problem is that the device claims to be a human interface device (HID).
So the linux usb hid driver (usbhid) tries to use it when it gets connected.
This fails and causes the device to disconnect and reconnect, which then repeats in a close loop (observe your syslog!).
In this state pyUSB can't find or use the device.

The solution is to tell the usbhid driver to ignore the device.
This can be done by addind a quirk option to the module when it gets loaded.
The easiest option is to add this line to your modprobe.d configuration (for example `/etc/modprobe.d/koshava.conf`):
```
options usbhid quirks=0x21c5:0x03e8:0x0004
```
And then reboot the computer. In case the module is compiled into the kernel you have to add this to your kernel command line:
```
usbhid.quirks=0x21c5:0x03e8:0x0004
```

## Install

You need:
 * python
 * [pyUSB](http://walac.github.io/pyusb/) (libusb-1.0)

### Install steps for Raspberry Pi / Debian
```
   apt-get install python python-setuptools
   easy_install pyusb
   git clone https://github.com/osteffen/koshava5-python.git
```
Then add `usbhid.quirks=0x21c5:0x03e8:0x0004` to your `/boot/cmdline.txt` (just append to the first line), save, and reboot.

Connect your Koshava5.

Use simple.py to read from the probe!

## Programs and Files

 - `koshava.py`: The code for communiating with the probe. Wrapped in a class called Koshava. Import this file in your scripts.
 - `simple.py`: A simple demo script that continuosly reads from the probe and prints to sdtout
 - `cli.py`: Command line tool that reads commands from stdin, talks to the probe and prints results
 - `server.py`: Same as `cli.py` but opens a TCP socket to use instaed of stdin/out. Can be used for remote monitoring.

## TODO

 - Complete the protocol. There are some more functions in the documentation and even some undocumented ones that are not implemented yet.

 - Implement support for different units. At the moment only "Tesla" works.

 - Make a GUI.
