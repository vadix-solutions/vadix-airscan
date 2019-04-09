#!/bin/bash
docker run --privileged -v $PWD:/buildozer/ -v /dev/bus/usb:/dev/bus/usb -v /etc/udev/rules.d/:/etc/udev/rules.d/ \
 	-v ~/keystores/:/keystores/ \
 	-e P4A_RELEASE_KEYSTORE=/keystores/vadix.keystore \
 	-e P4A_RELEASE_KEYSTORE_PASSWD=${KEYSTORE_PASS} \
 	-e P4A_RELEASE_KEYALIAS_PASSWD=${KEYALIAS_PASS} \
 	-e P4A_RELEASE_KEYALIAS=vdxairscan \
	vadix/buildozer buildozer android release deploy run
	