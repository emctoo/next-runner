#!/bin/bash

set -e

mkdir -p ~/.local/share/kservices5/
mkdir -p ~/.local/share/dbus-1/services/
mkdir -p ~/.local/bin/

cp "xg-runner.desktop"  ~/.local/share/krunner/dbusplugins/
cp "xg-runner.service" ~/.local/share/dbus-1/services/

kquitapp5 krunner

# TODO 应该有更好的方法
PID=$(procs -c disable --no-header runner.py | awk -F' ' '{print $1}')
echo "RUNNER PID: [${PID}]"

if [[ $PID ]]; then
    kill -9 "${PID}"
    echo "RUNNER KILLED, PID: [${PID}]"
fi
