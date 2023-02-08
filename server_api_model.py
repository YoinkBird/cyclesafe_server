from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import socketserver
import json
import cgi
import re
import os.path

from os import sys

# from modelgen.code, import routines for interacting with prediction model
#+ 'code' is a subdir because modelgen contains other resources as well. this is not best practice.
from modelgen.code import model

'''
Purpose: interface with prediction-model generation module
Other Documentation: see setup.sh
'''

# hard-coded globals
resource_dir = "res"
quiet = 0
selftest = 0
runhook = "./prepare_json.sh"

# mock storage
if( __name__ == '__main__' ):
    # kv of keys and file-paths
    keystore = {}

def gen_storage_key():
    import random
    # generate random key
    return random.randint(10000,
                          99999)
# TODO: rename to `filename`, since it's not a path
def gen_filepath_for_key( filepath, key="12346"):
    filepath = "%s_%s" % (filepath,key)
    return filepath

# update the model
# TODO: rename to:# def run_model_hook_legacy(hookpath):
def run_model_hook_legacy(hookpath):
    import os.path
    if (os.path.isfile(hookpath) ):
        from subprocess import call
        # https://stackoverflow.com/a/32084182
        # call(["ls","-ltr"])
        call(["bash" , hookpath])
    else:
        # TODO: need to return a status of some sort
        print("no hook found")

# pass geodata to model, get scores ( prediction results )
# input:
# * key : retrieve data for key:
# * * file-storage - retrieve data from filepath constructed from default filename and key
# * * db - retrieve data from db
# * filepath - retrieve data from filepath
# * key , filepath : retrieve data from filepath constructed from filepath and key
# TODO: pass-in the geodata
def get_model_results(**kwargs):
    # get data-structures which contain configs to control execution
    options_local, runmodels = model.get_global_configs()
    # vvv hacks for enabling import of model code vvv
    if(1):
        # new hack - functions depend on global var
        model.runmodels=runmodels
        # </mega_hack_runmodels>
    # ^^^ hacks for enabling import of model code ^^^

    # get geodata from passed-in args or from file
    geodata = -1
    if ( 'geodata' in kwargs ):
        geodata = kwargs['geodata']
    else:
        # update the filepath
        if ( 'filepath' in kwargs):
            filepath = kwargs['filepath']
#            print( f"get_model_results: filepath: {filepath}" )
            options_local['local_json_input'] = filepath
        # update the key and filepath-for-key
        if ( 'key' in kwargs):
            key = kwargs['key']
#            print( f"get_model_results: key: {key}" )
            # could be set to 'false'
            if ( key ):
                options_local['request_key'] = key
                options_local['local_json_input'] = gen_filepath_for_key( options_local['local_json_input'] , key)
        # load geodata
#        print( f"get_model_results: load geodata from {options_local['local_json_input']}" )
        geodata = load_json_file(options_local['local_json_input'])
    # load data, featdef, etc
    (data, data_dummies, df_int_nonan, featdef) = model.model_prepare(**options_local)
    # score the input data (paths are hard-coded within 'model', yay)
    response_json = model.score_manual_generic_route(data, data_dummies, df_int_nonan, featdef, geodata, **options_local)
    return response_json

# open json file
def load_json_file(filename):
    # tmp:
    filepath=("%s/%s" % (resource_dir, filename))
    # open file as json
    loadedjson = str()
    with open(filepath, 'r') as infile:
       loadedjson = json.load(infile)
    return loadedjson


# return json scored by model
#+ default filename and key
def retrieve_json_results( key ):
    # get_model_results will retrieve data by key, whether from file or db
    return get_model_results( key = key )

# wrapper to suppress 'filename' for any legacy calls
def retrieve_json_file(filename="gps_scored_route.json",key=False):
    return retrieve_json_results(key)

    # LEGACY:
    # dump json to file for consumption by whatever else needs it
    #+ default filename and key
    #+ TODO: this no longer relies on input file, for now just pass in nothing?
    #if ( quiet != 1):
    #    print("# save to file")
    # tmp:
    filepath=("%s/%s" % (resource_dir, filename))
    if ( quiet != 1):
        print("mock-response sending to : " + filepath)

    # make sure file is updated
    # run_model_hook_legacy(runhook)
    # get_model_results will retrieve data by key, whether from file or db
    return get_model_results( key = key )

    # open file as json
    # TODO: call the new function 'def load_json_file'
    loadedjson = str()
    with open(filepath, 'r') as infile:
       loadedjson = json.load(infile)

    # return json string
    return loadedjson

# save json to file for consumption by whatever else needs it
#+ in practice, not such a great idea, but for now it is what it is
#+ ultimately, the server needs to call the model anyway.
#+ will have to fix the encoding issues of converting to 2to3; not impossible, but super annoying
# return key
def save_json_file(response_json, filename, genkey=True):
    if ( quiet != 1):
        print("# save to file")
    # tmp: default filepath
    filepath=("%s/%s" % (resource_dir, filename))
    # generate key, update filepath accordingly
    key = gen_storage_key()
    # if key desired or passed in 
    if( genkey ):
        # if key passed in as int
        if( isinstance( genkey , int ) ):
            key = genkey
        filepath = gen_filepath_for_key( "%s/%s" % (resource_dir, filename) , key)
    if ( quiet != 1):
        print("response saving to : " + filepath)
    with open(filepath, 'w') as outfile:
       json.dump(response_json, outfile)

    # return some sort of success indicator, would probably have to try-catch though
    return (key, filepath)

        
# this section meant primarily for self-testing
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
        # store to file or data-structure
        mock_storage_to_file = 0
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
        # generate key
        key_generated = gen_storage_key()
        # if file-storage desired
        if( mock_storage_to_file == 1 ):
            key_generated, filepath_generated = save_json_file(mock_client_data, "gps_input_route.json")
            # briefly test hard-coding key for server
            # key_generated, filepath_generated = save_json_file(mock_client_data, "gps_input_route.json", 100001)
            pprint.pprint(
                    filepath_generated
                    )
        else:
            # if non-file storage desired:
            # hack mock data storage - save_json_file will still save file to disk
            keystore[ key_generated ] = mock_client_data
            pprint.pprint(
                key_generated
                )
        print("-------------------------")
        curtest="MOCK GET"
        print("-------------------------")
        print("%s - retrieving mock client data" % curtest)
        print("you have one job - return this string!")
        # used for GET
        #  note: would need to pass-in the key
        key_received = key_generated
        if( mock_storage_to_file == 1 ):
            message = get_model_results( key = key_received )
        else:
            message = get_model_results( geodata = keystore[ key_received ])
            pprint.pprint(
                message
                )
        print("-------------------------")
        # record files so they can be deleted easily. append file src: https://stackoverflow.com/a/4706520
        filepath_inferred = gen_filepath_for_key("gps_input_route.json",key_generated)
        with open("list_gen_gps_input_route_json.txt", "a") as myfile:
            myfile.write(filepath_inferred + "\n")
    # explicitely test runhook - otherwise this is covered by retrieve_json_file
    if ( selftest == 2):
        # run_model_hook_legacy(runhook)
        get_model_results()
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
* import modelgen - fixing path import
* import model.py (replace runhook)
* fix hacks from import model.py (hacks for enablement) - just diff against master and fix whatever is a hack

Current:
* file-IPC : remove all file references from model.py
* stop using files for information sharing


Future:

WorkLog:
steps for Current Work:

see <reporoot>/ ./t/cmds_dev.sh

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

- fix module import: removing redundant imports and moving into model-hook subroutine. setting up as '-post 2'
Remove dev-code for imports by viewing list of changes since before the imports were added:
    git diff 6910f78df06d2405406557762dfad5a4e5a0c872 server_api_model.py
    loop through lines of potentially unnecessary imports:
        comment line(s) # rely on git add -p to track progress
        ./t/cmds_dev.sh
        if fail: uncomment, mark for debug
        if pass: git add -p
    end_loop
    remove all commented based on git diff --cached

- fix module import: move all path setup,etc into __init__.py
this is already partially implemented;
in this file remove the line:
sys.path.append("./modelgen/code")
in modelgen repo, just stash pop

- fix runhook using model, i.e. replace the call to external hook with direct model gen calls
remove the enablement-workarounds from ./t/cmds_dev.sh

something wrong with server after converting runhook.
* Verified that model still works when directly called (after setting up the test-input file)
* Verified that old runhook works.
* Verified that post works (self-test of server_api_model.py)
* * ./t/cmds_dev.sh
trying again
issue: gps_scored_route.json not getting created, i.e. model scoring not running
=> ugh. still had the "if __file__ eq 'main'" in the runhook code. baka.

---------------------------------------
- file-IPC: remove files for infosharing
1. move all file references from model.py
convert model.py to have the data simply passed in and to return data
  start in model.py by having all file-paths abstracted down into "if main"
have server_api_model.py make these calls
2. 

- keystore : generate random key for post, use for storage and then return. pass in key for get to retrieve
verified in server.server_api_model.py (local) 
TODO: implement, verify in server.server.py (web)
phases:
1. [x] server-side: implement static key storage (global var)
1b server-side: return key to client
2. client-side: extract key from response, send in next request
2b: server-side: use request-key (deactivate static keys)
3: server-side: global dict to store keys and json (no more files)
3b: [x] server.server_api_model.py : global dict to store keys and json (no more files)
4: server-side: sqlite db ( no more global dict )
'''
