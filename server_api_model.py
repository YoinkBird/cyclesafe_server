from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import socketserver
import json
import cgi
import re
import shutil
import os.path

# import modelgen.code 
from modelgen import * # works
from modelgen.code import *
from modelgen.code import helpers # works
from os import sys

# start here: https://stackoverflow.com/questions/50598995/how-do-i-import-all-functions-from-a-package-in-python
#+ TODO: move into modelgen's __init__.py 
sys.path.append("./modelgen/code")
from modelgen.code import model #  works, now that sys.path.append has the correct path. I certainly was tired...

from modelgen.code.model import score_manual_generic_route # works!
from modelgen.code.model import * # works!
# vvv temporary, just to test the import vvv
if ( 0 and __name__ == '__main__'):
    # load data, featdef, etc
    # global options
    options = {
            'graphics' : 0, # 0 - disable, 1 - enable
            'verbose' : 0, # -1 - absolutely silent 0 - minimal info, 1+ - increasing levels
            }
    # choose which model to run
    runmodels = {}
    # essential options for route-scoring service
    # disable only temporarily to avoid filling up jupyter qtconsole buffer while trying to interpret results of previous runs
    if(1):
        runmodels['score_manual_generic_route'] = 1
        runmodels['map_generate_human_readable_dectree'] = 1
        runmodels['map_manual_analyse_strongest_predictors'] = 0
    # new hack - functions depend on global var
#    model.store_opt_runmodels(runmodels)
    model.runmodels=runmodels
    # localise options, avoid accidental dependencies in other functions
    options_local = options
    del(options)
    ################################################################################
    # PREPROCESS
    ################################################################################
    # load data, featdef, etc
    (data, data_dummies, df_int_nonan, featdef) = model_prepare(**options_local)
    ################################################################################
    # /PREPROCESS
    ################################################################################
    score_manual_generic_route(data, data_dummies, df_int_nonan, featdef, **options_local)
# ^^^ temporary, just to test the import ^^^

#from modelgen.code import model
#import modelgen.code.helpers
#from modelgen.code.helpers import *
#from modelgen.code.feature_definitions import *
#from modelgen.code.txdot_parse import *

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
    # time for self-test?
    if len(argv) >= 2:
        # power-on self-test
        if(argv[1] == "-post"):
            selftest = 1
            # levels - only if 3 args and is digit, avoid accidents later when proper argparsing implemented
            if ( len(argv) == 3 and argv[2].isdigit() ):
                selftest = int(argv[2])
    
    # test load,return
    import pprint
    if ( selftest == 1):
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
    # explicitely test runhook - otherwise this is covered by retrieve_json_file
    if ( selftest == 2):
        run_model_hook(runhook)
    # intentionally fail for testing purposes by calling non-existing function
    if ( selftest == 3):
        print("intentionally fail by calling non-existing function")
        qwazantch()
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
* enable self-test
* enable import of model.py (fix all runtime issues)

Current:


Future:
* import model.py (replace runhook)
* fix hacks from import model.py (hacks for enablement) - just diff against master and fix whatever is a hack

WorkLog:
steps for Current:

# re-setup all links:
./setup.sh clean
./setup.sh prepare
# run self-test code
python3 server_api_model.py -post 1


notes
- gps_input_route_test.json quite outdated, needed to link back to the one used for curl testing:
ln -sf ../modelgen/t/route_json/gps_generic.json res/gps_input_route_test.json

- setup.sh - added 'prepverif' mode to list the various symlinks and reduce confusion

- had to add new routine for loading test-json from disk; when testing directly through server this is done in setup.sh using a curl command

- "mock post" working - diff res.good/gps_input_route.json res/gps_input_route.json

- enable "mock get"

- setup.sh - added commands for symlink setup and removal of test-file gps_input_route_test.json 

- adding cli options to control levels of self-testing

- fixing module import of model.py, albeit with hacks

- fixing model.py relative paths. model.py was always run from specific relative dir, therefore many relpaths were introduced which now need to be fixed

'''
