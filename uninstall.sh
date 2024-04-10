#!/bin/bash

set -e

rm ~/.local/share/krunner/dbusplugins/xg-runner.desktop
rm  ~/.local/share/dbus-1/services/xg-runner.service

kquitapp5 krunner
