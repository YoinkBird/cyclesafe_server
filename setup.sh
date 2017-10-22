# prepare
## clone into dir with model as a subdir. this keeps all filepaths relative

## files from model:
### ln should be safe, haven't seen server overwrite the files
ln -sf ../../output/gps_scored_route.json res/

# startup - use python2, ran into encoding errors when converting to python3 after 2to3
python2 ./server.py 8009 

# mock client map-ui - upload json
#+ src: https://stackoverflow.com/a/7173011
curl --header "Content-Type: application/json" http://localhost:8009 --data @../t/route_json/gps_generic.json

# mock client map-ui - retrieve json
http://localhost:8009

