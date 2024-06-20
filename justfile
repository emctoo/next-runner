install: uninstall
  cp next-runner.desktop ~/.local/share/krunner/dbusplugins/next-runner.desktop 
  cp next-runner.service ~/.local/share/dbus-1/services/next-runner.service

uninstall:
  rm -rf ~/.local/share/krunner/dbusplugins/next-runner.desktop 
  rm -rf ~/.local/share/dbus-1/services/next-runner.service
  kquitapp5 krunner

watch-and-kill:
  watchexec -w . -e py -- just kill

watch-runner-process:
  procs -c disable xg\/runner\.py -w -W 1

get-pid:
  @ps -ef | rg -i -e '.*python.*xg\/runner\.py'
  @ps -ef | rg -i -e '.*python.*xg\/runner\.py' | awk -F' ' '{print $2}'

get-running:
  @ps -ef | rg -i -e '.*xg\/runner\.py'

nothing:
  # procs -c disable --no-header runner.py | awk -F' ' '{print $1}'
  # procs -c disable --no-header runner.py
 
kill:
  #!/usr/bin/env bash

  PID=$(ps -ef | rg -i -e '.*python.*xg\/runner\.py' | awk -F' ' '{print $2}')
  if [[ -z $PID ]]; then
    echo "process not found"
  else
    kill $PID
    echo "process $PID killed"
  fi

