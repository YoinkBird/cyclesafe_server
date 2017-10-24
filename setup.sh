set -ev
# prepare
## clone into dir with model as a subdir. this keeps all filepaths relative
# cd <parentProjDir> && git clone ... server
# manually verify that 'server' is in the .gitignore of the parent project

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

#-------------------------------------------------------------------------------- 
# mock client map-ui - upload json
#+ src: https://stackoverflow.com/a/7173011
curl --header "Content-Type: application/json" http://localhost:8009 --data @../t/route_json/gps_generic.json

#-------------------------------------------------------------------------------- 
# mock client map-ui - retrieve json
curl http://localhost:8009

#-------------------------------------------------------------------------------- 
# mock client map-ui - view json in browser
chromium-browser --incognito http://localhost:8009
# how about some other things?
chromium-browser --incognito directions.html directions_markers.html

#-------------------------------------------------------------------------------- 
# how to kill the server
lsof -i :8009 | tee -a server_pid_lsof.txt
# show any running servers
cat server_pid.txt
cat server_pid_lsof.txt
