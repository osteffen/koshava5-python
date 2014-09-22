#!/bin/bash
echo "This script will unload the usb hid driver."
echo "While the driver is not loaded, you can plug in the Koshava5 USB Probe"
echo "During this time USB Keyboards and mice will not work!"
echo "The driver will be reloaded after 10 seconds."
echo "Press ENTER to continue"
read

echo "Unloading usb hid driver."
rmmod usbhid

echo "Plug in the Koshava5. Driver will be reloaded in"

for i in {10..1}; do
    echo -n "$i  "
    sleep 1
done

echo ""
echo "Loading driver..."
modprobe usbhid
echo "Done!"
