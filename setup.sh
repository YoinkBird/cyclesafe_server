
set -e
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

# FUNCTIONALITY
# setup.sh prepares the env by symlinking to files required by the model generation code so the server can accept user input, pass to modelgen, return to user. 
# 
# preparation phase
# implement symlinks for communication between server and modelgen ("pseudo IPC")
#
# launch phase
# run the server in background, record the PID
# note: the server code is now able to close port if it gets interrupted
#
# verify phase
# test the server, then launch browser window to use the server 
# testing is a completely visual-inspection process; no validation of the results is done.
# test1 is performed by uploading json and downloading the scored response
# test2 is performed by launching a browser window so the tester can interactively verify that the website is functioning correctly.

# IMPLEMENTATION OF ROUTE SCORING
# NOTE: current implementation only good for one session at a time due to reliance on (meta) physical json files being dumped to disk. 
#
# preparation via setup.sh
# First and foremost: This implementation is a hack done to get the demo up and running in a personal dev environment. These comment-strings are just the documentation to avoid confusion as this "requirements as hacky scripts" is converted into code.
# The preparation step enables pseudo-IPC by allowing server and modelgen to pass data without following good design practices (in order to rapidly set up an MVP).
# The preparation step creates links between required input/output json files such that server and model are "communicating" without being directly connected in any way.
# server dumps json for modelgen to consume or reads json generated by server
# modelgen consumes input json and generates output json
#
# route scoring via server.py and prepare_json.sh
# the server calls prepare_json.sh , which is just a wrapper to run the model generation code.
# this preserves some semblance of good design even though all of this is just a big ole hack.
# fortunately, this approach does mean that the server code already sees json generation as an abstraction, a deliberate design decision made so that this hacky "pseudo IPC" could be easily fixed in future without having to overcome strong bindings everywhere.


curdir=$(dirname $0)
cd $curdir

runall=1
if [[ $# -gt 0 ]]; then
  step=$1; shift;
  runall=0
fi

if [[ ${runall} -eq 1 ]]; then
  step="prepare";
fi
# # backwards compatibility - launch used to include compare
# if [[ ${step} == "launch" ]]; then
#   step="prepare";
# fi

modelgendir="modelgen";
if [ ! -e ${modelgendir} ] || [ ! -d ${modelgendir} ] ; then
  echo "-E- : model generation repo likely not set up correctly";
  echo "-E- : ensure that directory [ $modelgendir ] contains the repo for generating the prediction model";
  exit;
fi

# remove the generated files and links
if [[ ${step} == "clean" ]]; then
  dbecho="echo"
  dbecho=""
  # these paths link back to the current dir for server, as of now
  # server links
  $dbecho rm -v -f ./res/gps_scored_route.json
  # server files
  $dbecho rm -v -f ./res/gps_input_route.json

  # model links 
  $dbecho rm -v -f ./${modelgendir}/output/gps_input_route.json
  # model files
  $dbecho rm -v -f ./${modelgendir}/output/gps_scored_route.json

  # visually verify
  pwd
  git clean -xdn
  cd ./${modelgendir}
  pwd
  git clean -xdn
  cd ..
fi

if [[ ${step} == "prepare" ]]; then
  # single entry point from model to server, i.e. links go through <modeldir>/server
  #+ ./${modelgendir}/server -> ../
  set +e
  ln -s ../ ${modelgendir}/server
  set -e
  ## files from model:
  #// ln should be safe, haven't seen server overwrite the files
  ### output from server to model : the map json route received from web
  #+ link: ./${modelgendir}/output -> ../'server'/res/gps_input_route.json ( using 'server' symlink)
  #+ link: ./${modelgendir}/output -> ../../res/gps_input_route.json       ( without 'server' symlink)
  if [ ! -r  ./res/gps_input_route.json ]; then
    ln -v -s ../server/res/gps_input_route.json ./${modelgendir}/output/ # || echo "couldn't create symlink"
    ls -lts ./${modelgendir}/output/gps_input_route.json # || echo "couldn't create symlink"
  fi
  ### input to server from model : the scored json route scored by the model
  #+ link: ./res/gps_scored_route.json -> ../${modelgendir}/output/gps_scored_route.json
  if [ ! -r ./${modelgendir}/output/gps_scored_route.json ]; then
    ln -v -s ../${modelgendir}/output/gps_scored_route.json ./res/ # || echo "couldn't create symlink"
    ls -lts ./res/gps_scored_route.json # || echo "couldn't create symlink"
  fi

  if [[ ${runall} -eq 1 ]]; then
    step="launch"
  fi
fi

if [[ ${step} == "launch" ]]; then

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
  curl -w "http_code:[%{http_code}]" --header "Content-Type: application/json" http://localhost:8009/rest/score/upload --data @${modelgendir}/t/route_json/gps_generic.json

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
