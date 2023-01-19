
set -e
# PREPARE:
## clone this repo as the top-level dir, as it will clone the model generation into a subdir
# cd <writeable path> && git clone <url> 
# manually verify that 'modelgen' is in .gitignore , as this is the default path to the model generation repo

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

# WORKLOG CONTAINERISATION
# TODO: 1. convert this script to use vanilla Docker commands instead of current linux-based methodology
# TODO: 2. convert to use docker-compose


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

# container information
docker_user="yoinkbird"
app_name_server="cs_server"
container_tag_server="latest"
container_name_server="${docker_user}/${app_name_server}"
app_name_modelgen="cs_modelgen"
container_tag_modelgen="latest"
container_name_modelgen="${docker_user}/${app_name_modelgen}:${container_tag_modelgen}"

# TODO: build server container - provisional step to enable containerisation
# ...

# TODO: not working yet. pull - obtain modelgen artifact, provisional hacky methodology to locate either from registry or simply from localhost
if [[ 1 -eq 0 ]] && [ ${step} != "clean" ] && [ ${step} != "reset" ] ; then
  set +e
  docker pull ${container_name_modelgen} > /dev/null 2>&1
  if [[ $? -ne 0 ]]; then
    echo "WARN: could not pull ${container_name_modelgen}"
    echo "DEV: checking whether image exists locally"
  fi
  # DEV: redundant if already pulled, but useful if only developing locally
  docker inspect "${container_name_modelgen}" > /dev/null 2>&1
  if [[ $? -ne 0 ]]; then
    echo "FATAL: image ${container_name_modelgen} cannot be found"
    exit 1
  else
    echo "INFO: obtained image ${container_name_modelgen}"
  fi
  set -e
fi

modelgendir="modelgen";
modelgenbranch="containerize";
# check whether modelgen repo exists, clone as needed unless during the cleanup steps (clean and reset)
if [ ! -e "${modelgendir}/.git/config" ] && [ ${step} != "clean" ] && [ ${step} != "reset" ] ; then
  # get the host of the repo
  #+ process 'show origin' with perl to get the fetch/clone url,
  #+ then extract the github/username from that url
  github_host_repo_origin=$(git remote show origin | perl -nle 'm|Fetch URL: (.*)| && print $1' )
  github_host_user=$( dirname ${github_host_repo_origin} )
  github_url_modelgen="${github_host_user}/cyclesafe";
  # path exists but is not directory
  if [ -e ${modelgendir} ] && [ ! -d ${modelgendir} ] ; then
    echo "-E- : model generation repo likely not set up correctly";
    echo "-E- : ensure that directory [ $modelgendir ] contains the repo for generating the prediction model";
    exit;
    # path does not exist
  elif [ ! -e ${modelgendir} ] ; then
    # try to set up
    # simple: not cloned yet
    set -x
    git clone ${github_url_modelgen} ${modelgendir};
    # HARD_CODE
    cd ${modelgendir} && git checkout ${modelgenbranch} && cd -
    set +x 
    if [ $? -ne 0 ]; then
      echo "-E- : could not clone the repo";
    fi
  fi
fi

# remove the generated files and links
if [[ ${step} == "clean" ]] || [[ ${step} == "reset" ]]; then
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

  # hard-clean
  if [[ ${step} == "reset" ]]; then
    rm -rf ${modelgendir};
  fi

  # visually verify
  pwd
  git clean -xdn
  if [ -e ${modelgendir} ]; then
    cd ./${modelgendir}
    pwd
    git clean -xdn
    cd ..
  fi
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
    step="build"
  fi
fi

# build server container - provisional step to enable containerisation
if [[ "${step}" == "build" ]]; then
  docker build --tag ${container_name_server} .

  if [[ ${runall} -eq 1 ]]; then
    step="launch"
  fi
fi

set -u
urlAddress="http://localhost"
urlPort="8009"
jsonEndpoint="rest/score";
urlJsonServer="${urlAddress}:${urlPort}" # window.location.origin + '/rest/score'
urlJsonServerRest="${urlJsonServer}/${jsonEndpoint}" # window.location.origin + '/rest/score'
urlJsonServerRestPost="${urlJsonServerRest}""/""upload";
urlJsonServerRestGet="${urlJsonServerRest}""/""retrieve";

if [[ ${step} == "launch" ]]; then


  # startup
  # if 'docker: Error response from daemon: driver failed programming external connectivity on endpoint cs_server_8009 (64c7...): Bind for 0.0.0.0:8009 failed: port is already allocated.', could just be from re-running
  docker run -d -p ${urlPort}:8009 --name "cs_server_${urlPort}" ${container_name_server}
  # was already useless # server_pid=$!
  echo $?
  # if server already running, the new PID just gets confusing
  #echo $! >> server_pid.txt

  # let it spin up
  sleep 1

  # how to kill the server
  lsof -i :${urlPort} | tee -a server_pid_lsof.txt

  if [[ ${runall} -eq 1 ]]; then
    step="verify"
  fi
fi


# TODO: remove provisional exit once containerisation is complete
exit 1

if [[ ${step} == "verify" ]]; then
  #-------------------------------------------------------------------------------- 
  echo "VERIFY POST:"
  # mock client map-ui - upload json
  #+ src: https://stackoverflow.com/a/7173011
  curl -w "http_code:[%{http_code}]" --header "Content-Type: application/json" ${urlJsonServerRestPost} --data @${modelgendir}/t/route_json/gps_generic.json

  #-------------------------------------------------------------------------------- 
  echo "VERIFY GET:"
  # mock client map-ui - retrieve json
  curl -w "http_code:[%{http_code}]" ${urlJsonServerRestGet}

  #-------------------------------------------------------------------------------- 
  echo "VERIFY GET HTML:"
  # mock client map-ui - retrieve json
  curl -w "http_code:[%{http_code}]" --output /dev/null ${urlJsonServer}/directions.html

  if [[ ${runall} -eq 1 ]]; then
    step="browser"
  fi
fi

if [[ ${step} == "browser" ]]; then
  # browser_and_args="chromium-browser --incognito"
  browser_and_args="firefox --private-window"
  #-------------------------------------------------------------------------------- 
  # mock client map-ui - view json in browser
  ${browser_and_args[@]} ${urlJsonServerRestGet}
  # how about some other things?
  # TODO: convert to host-specific call, i.e. http://localhost:8009/directions.html
  ${browser_and_args[@]} ${urlJsonServer}/directions.html # http://localhost:8009/directions_markers.html
fi

# stop the server. naming this step kill because it's using 'kill' instead of cleanly shutting down server
if [[ ${step} == "kill" ]]; then
  echo "stopping server via kill"
  killed=0
  for pid in $(cat server_pid_lsof.txt  | awk '{printf "%s\n", $2}' | perl -nle 'm|(\d+)| && print $1'); do
    set +e
    # UID        PID  PPID  C STIME TTY      STAT   TIME CMD
    # myusern+ 23837  9337  0 17:09 pts/3    S      0:00 python3 ./server.py <urlPort>
    ps -fww $pid | grep "${pid}.*python3.*server\.py.*${urlPort}";
    rc=$?
    if [[ $rc -eq 0 ]]; then
      set -x
      kill -s HUP ${pid}
      set +x
      killed=1
    fi
    set -e
  done
  if [[ $killed -eq 1 ]]; then
    set -x
    rm server_pid_lsof.txt
    set +x
  else
    echo "could not kill server"
  fi
fi

#-------------------------------------------------------------------------------- 
# show any running servers
#cat server_pid.txt
cat server_pid_lsof.txt
