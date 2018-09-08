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
    loadedjson = str()
    with open(filepath, 'r') as infile:
       loadedjson = json.load(infile)

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
        print("-------------------------")
        print("you have one job - return this string!")
        message = retrieve_json_file()
        pprint.pprint(
                message
                )
        print("-------------------------")
        # test save - depends on load
        print("-------------------------")
        print("you have one job - save this string!")
        pprint.pprint(
                save_json_file(message, "gps_input_route_test.json")
                )
        print("-------------------------")
    # make sure file is updated
    if ( selftest >= 1):
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
WorkLog:
Done:
* save server.py as server_api_model.py , remove all server code

Current:
* in server.py, remove model-specific code and import server_api_model


Future:
* import model.py

'''
