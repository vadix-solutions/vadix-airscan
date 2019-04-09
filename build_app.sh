#!/bin/bash
if [ "$1" == "release" ]; then
    docker run --privileged -v $PWD:/buildozer/ -v /dev/bus/usb:/dev/bus/usb -v /etc/udev/rules.d/:/etc/udev/rules.d/ \
        -v ~/keystores/:/keystores/ \
        -e P4A_RELEASE_KEYSTORE=/keystores/vadix.keystore \
        -e P4A_RELEASE_KEYSTORE_PASSWD=${KEYSTORE_PASS} \
        -e P4A_RELEASE_KEYALIAS_PASSWD=${KEYALIAS_PASS} \
        -e P4A_RELEASE_KEYALIAS=vdxairscan \
        vadix/buildozer buildozer android release deploy run
else
    echo "Running debug build - call with 'release' argument to build release"
    docker run --privileged -v $PWD:/buildozer/ -v /dev/bus/usb:/dev/bus/usb -v /etc/udev/rules.d/:/etc/udev/rules.d/ \
        vadix/buildozer buildozer android debug deploy run logcat
fi
	