#!/bin/bash

# Small utility to kill krunner (and, by extension, restart it with updated plugins). 
# Thankfully taken from https://github.com/alex1701c/krunner-vscodeprojects/blob/master/postinst

if pgrep -x krunner > /dev/null; then
    killall krunner
fi
