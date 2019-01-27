#!/bin/sh

#changing file permissions
chmod a+x bin/Cool-Retro-Term-1.1.1-x86_64.AppImage
chmod a+x launch.py

current="$(pwd)/launch.py"
echo $current
./bin/Cool-Retro-Term-1.1.1-x86_64.AppImage --fullscreen --profile "Monochrome Green" -T "PUNICS ©1979 DO NOT DISTRIBUTE" -e "${current}"
