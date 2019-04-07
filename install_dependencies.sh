#!/bin/bash

echo "Installing dependencies"
sudo apt install \
	python-pip \
	build-essential \
	git \
	python3 \
	python3-dev \
	ffmpeg \
	libsdl2-dev \
	libsdl2-image-dev \
	libsdl2-mixer-dev \
	libsdl2-ttf-dev \
	libportmidi-dev \
	libswscale-dev \
	libavformat-dev \
	libavcodec-dev \
	zlib1g-dev \
	libgstreamer1.0 \
	gstreamer1.0-plugins-base \
	gstreamer1.0-plugins-good

echo "Adding i386 architecture and installing more dependencies.."
sudo dpkg --add-architecture i386
sudo apt-get install build-essential ccache \
	libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 \
	libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 \
	python2.7 python2.7-dev openjdk-8-jdk unzip zlib1g-dev zlib1g:i386

echo "Done!"