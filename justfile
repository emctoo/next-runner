
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

