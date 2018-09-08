from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import socketserver
import json
import cgi
import re
import shutil
import os.path


'''
Purpose: interface with prediction-model generation module
Other Documentation: see setup.sh
'''

# hard-coded globals
resource_dir = "res"
quiet = 0
selftest = 0
runhook = "./prepare_json.sh"

# update the model
def run_model_hook(hookpath):
    import os.path
    if (os.path.isfile(hookpath) ):
        from subprocess import call
        # https://stackoverflow.com/a/32084182
        # call(["ls","-ltr"])
        call(["bash" , hookpath])
    else:
        # TODO: need to return a status of some sort
        print("no hook found")

# open json file
def load_json_file(filename):
    # tmp:
    filepath=("%s/%s" % (resource_dir, filename))
    # open file as json
    loadedjson = str()
    with open(filepath, 'r') as infile:
       loadedjson = json.load(infile)
    return loadedjson


# dump json to file for consumption by whatever else needs it
def retrieve_json_file(filename="gps_scored_route.json"):
    #if ( quiet != 1):
    #    print("# save to file")
    # tmp:
    filepath=("%s/%s" % (resource_dir, filename))
    if ( quiet != 1):
        print("mock-response sending to : " + filepath)
    # with open(filepath, 'w') as outfile:
    #    json.dump(response_json, outfile)

    # make sure file is updated
    run_model_hook(runhook)

    # open file as json
    # TODO: call the new function 'def load_json_file'
    loadedjson = str()
    with open(filepath, 'r') as infile:
       loadedjson = json.load(infile)

    # TODO: refactor out ; not used anywhere
    # read into python structure - TODO: not best practice, return json string instead?
    loadedroute = json.loads(loadedjson)

    # deprecated, meant for verification
    # return_value = -1
    # verify
    # if( response_json == loadedjson ):
    #     print("json string resurrected successfully")
    #     return_value = 1
    # compare the dict if possible?

    # return json string
    return loadedjson

# save json to file for consumption by whatever else needs it
#+ in practice, not such a great idea, but for now it is what it is
#+ ultimately, the server needs to call the model anyway.
#+ will have to fix the encoding issues of converting to 2to3; not impossible, but super annoying
def save_json_file(response_json, filename):
    if ( quiet != 1):
        print("# save to file")
    # tmp:
    filepath=("%s/%s" % (resource_dir, filename))
    # if ( quiet != 1):
    #     print("mock-response sending to : " + filepath)
    with open(filepath, 'w') as outfile:
       json.dump(response_json, outfile)

    # open file as json
    # loadedjson = str()
    # with open(filepath, 'r') as infile:
    #    loadedjson = json.load(infile)

    # loadedroute = json.loads(loadedjson)

    # deprecated, meant for verification
    # return_value = -1
    # verify
    # if( response_json == loadedjson ):
    #     print("json string resurrected successfully")
    #     return_value = 1
    # compare the dict if possible?

    # return some sort of success indicator, would probably have to try-catch though
    return filename

        
# 
if __name__ == "__main__":
    from sys import argv
    
    # test load,return
    import pprint
    if ( selftest >= 1):
        # self-test strategy:
        # simulate POST followed by GET
        # "seed" the POST with a local test json, same as used in setup.sh to test server using curl and post
        print("-------------------------")
        curtest="MOCK POST"
        print("%s - loading mock client data" % curtest)
        mock_client_data = load_json_file("gps_input_route_test.json")
        # test saving received data to disk
        print("-------------------------")
        print("%s - submitting mock client data" % curtest)
        print("you have one job - save this string!")
        # used for POST
        pprint.pprint(
                save_json_file(mock_client_data, "gps_input_route.json")
                )
        print("-------------------------")
        curtest="MOCK GET"
        print("-------------------------")
        print("%s - retrieving mock client data" % curtest)
        print("you have one job - return this string!")
        # used for GET
        message = retrieve_json_file()
        pprint.pprint(
                message
                )
        print("-------------------------")
    # make sure file is updated
    if ( selftest >= 1):
    # test runhook - this is covered by retrieve_json_file
    if ( selftest == 0):
        run_model_hook(runhook)
    # vvv intentionally fail for testing purposes vvv
    # qwazantch()
    # /test
        


# notes on python3 conversion
## reading headers and using 'encode()'
# src: https://stackoverflow.com/a/2124520

## returning file after loading
# src: https://stackoverflow.com/a/45152020

# vvv didn't work:
# <open file 'directions.html', mode 'r' at 0x7f0a35cbb6f0>
# self.wfile.write( file )
# vvv no longer works (python2 only, arguably not the best method at the time):
# src: https://gist.github.com/tliron/8e9757180506f25e46d9#file-rest-py-L136
# shutil.copyfileobj( file, self.wfile )


'''
Planning:
Done:
* save server.py as server_api_model.py , remove all server code
* in server.py, remove model-specific code and import server_api_model

Current:
* enable self-test


Future:
* import model.py

WorkLog:
steps for Current:

# re-setup all links:
./setup.sh clean
./setup.sh prepare
# run self-test code
python3 server_api_model.py


notes
- gps_input_route_test.json quite outdated, needed to link back to the one used for curl testing:
ln -sf ../modelgen/t/route_json/gps_generic.json res/gps_input_route_test.json

- setup.sh - added 'prepverif' mode to list the various symlinks and reduce confusion

- had to add new routine for loading test-json from disk; when testing directly through server this is done in setup.sh using a curl command

- "mock post" working - diff res.good/gps_input_route.json res/gps_input_route.json

- enable "mock get"

- setup.sh - added commands for symlink setup and removal of test-file gps_input_route_test.json 

'''
