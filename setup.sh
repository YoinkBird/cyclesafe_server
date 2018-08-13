set -ev
# PREPARE:
## clone into dir with model as a subdir. this keeps all filepaths relative
# cd <parentProjDir> && git clone ... server
# manually verify that 'server' is in the .gitignore of the parent project

# USAGE:
# launch server, verify running from cli, and launch browser to interact:
# $0
# launch server only:
# $0 launch
#
# verify only, useful during development (if server already running):
# $0 verify
#
# browser only, useful during development (if server already running):
# $0 browser

curdir=$(dirname $0)
cd $curdir

runall=1
if [[ $# -gt 0 ]]; then
  step=$1; shift;
  runall=0
fi

if [[ ${runall} -eq 1 ]]; then
  step="launch";
fi

if [[ ${step} == "launch" ]]; then

  ## files from model:
  #// ln should be safe, haven't seen server overwrite the files
  ### output from server to model : the map json route received from web
  if [ ! -r  ./res/gps_input_route.json ]; then
    ln -s ../server/res/gps_input_route.json ../output/ # || echo "couldn't create symlink"
  fi
  ### input to server from model : the scored json route scored by the model
  if [ ! -r ../output/gps_scored_route.json ]; then
    ln -s ../../output/gps_scored_route.json res/ # || echo "couldn't create symlink"
  fi

  # startup - use python2, ran into encoding errors when converting to python3 after 2to3
  # if 'port already in use', could just be from re-running
  python2 ./server.py 8009 &
  server_pid=$!
  echo $?
  # if server already running, the new PID just gets confusing
  #echo $! >> server_pid.txt

  # let it spin up
  sleep 1

  # how to kill the server
  lsof -i :8009 | tee -a server_pid_lsof.txt

  if [[ ${runall} -eq 1 ]]; then
    step="verify"
  fi
fi
if [[ ${step} == "verify" ]]; then
  #-------------------------------------------------------------------------------- 
  # mock client map-ui - upload json
  #+ src: https://stackoverflow.com/a/7173011
  curl -w "http_code:[%{http_code}]" --header "Content-Type: application/json" http://localhost:8009/rest/score/upload --data @../t/route_json/gps_generic.json

  #-------------------------------------------------------------------------------- 
  # mock client map-ui - retrieve json
  curl -w "http_code:[%{http_code}]" http://localhost:8009/rest/score/retrieve
  if [[ ${runall} -eq 1 ]]; then
    step="browser"
  fi
fi

if [[ ${step} == "browser" ]]; then
  #-------------------------------------------------------------------------------- 
  # mock client map-ui - view json in browser
  chromium-browser --incognito http://localhost:8009/rest/score/retrieve
  # how about some other things?
  # TODO: convert to host-specific call, i.e. http://localhost:8009/directions.html
  chromium-browser --incognito http://localhost:8009/directions.html http://localhost:8009/directions_markers.html
fi

#-------------------------------------------------------------------------------- 
# show any running servers
#cat server_pid.txt
cat server_pid_lsof.txt
