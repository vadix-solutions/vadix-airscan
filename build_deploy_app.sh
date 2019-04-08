#!/bin/bash
docker build -t vadix/buildozer .
docker run --privileged -v $PWD:/buildozer/ -v /dev/bus/usb:/dev/bus/usb -v /etc/udev/rules.d/:/etc/udev/rules.d/ vadix/buildozer buildozer android release deploy run