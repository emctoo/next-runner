default:
  just --list

# restart krunner service
restart-krunner:
  systemctl --user restart plasma-krunner.service

# install all files
install: uninstall
  # mkdir -p ~/.local/share/kservices5/
  # cp next-runner.desktop ~/.local/share/kservices5/next-runner.desktop 

  mkdir -p ~/.local/share/krunner/dbusplugins/
  cp next-runner.desktop ~/.local/share/krunner/dbusplugins/next-runner.desktop 

  mkdir -p ~/.local/share/dbus-1/services/
  cp next-runner.service ~/.local/share/dbus-1/services/next-runner.service

  # kquitapp6 krunner
  just restart-krunner

  # restart the dbus sevice by killing it
  just kill

# uninstall service
uninstall:
  rm -rf ~/.local/share/krunner/dbusplugins/next-runner.desktop 
  rm -rf ~/.local/share/dbus-1/services/next-runner.service
 
  # kquitapp6 krunner
  just restart-krunner

# watch the process and kill it when python file changes
watch-and-kill:
  watchexec -w . -e py -- just kill

# watch "/next-runner/runner.py" process
watch-runner-process:
  procs -c disable \/next-runner\/runner\.py -w -W 1

get-pid:
  @ps -ef | rg -i -e '.*python.*next\-runner\.py'
  @ps -ef | rg -i -e '.*python.*next\-runner\.py' | awk -F' ' '{print $2}'

get-running:
  @ps -ef | rg -i -e '.*next\-runner\.py'

_not-working:
  # procs -c disable --no-header runner.py | awk -F' ' '{print $1}'
  # procs -c disable --no-header runner.py
 
kill:
  #!/usr/bin/env bash

  PID=$(ps -ef | rg -i -e '.*python.*\/next\-runner\/runner\.py' | awk -F' ' '{print $2}')
  if [[ -z $PID ]]; then
    echo "process not found"
  else
    kill $PID
    notify-send 'Next killed!' "process $PID killed" --icon=dialog-information
  fi

