# vadix-airscan
A lightweight and clean app used to detect invasive video surveillance in guest accommodations

## Installation

First, install the building dependencies - please review the content of this script before you run it.

```./install_dependencies.sh```

Now prepare the python virtual environment for Kivy development

```./build_environment.sh``

## Coding the app

Follow the Kivy guides

The source code is in the 'airscan' folder.

## Building and deploying the app

docker run --privileged -v $PWD:/buildozer/ -v /dev/bus/usb:/dev/bus/usb -v /etc/udev/rules.d/:/etc/udev/rules.d/ vadix/buildozer buildozer android debug deploy run



# Credits

Success/Danger icons provided by PngTree.com ([free icons](https://pngtree.com/free-icon) from pngtree.com)