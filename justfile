
watch-code:
  watchexec -e py -r -c -- just kill

watch-runner-process:
  procs xg -w -W 1

get-pid:
  ps -ef | rg -i -e '.*python.*runner\.py' | awk -F' ' '{print $2}'

  # procs -c disable --no-header runner.py | awk -F' ' '{print $1}'
  # procs -c disable --no-header runner.py
 
kill:
  kill -9 $(ps -ef | rg -i -e '.*python.*runner\.py' | awk -F' ' '{print $2}')

