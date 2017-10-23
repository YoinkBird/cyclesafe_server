from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import cgi

# hard-coded globals
resource_dir = "res"
quiet = 0
selftest = 1
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

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        # TODO: Allow-Origin has to be a domain-name in prod!
        #+ src: https://stackoverflow.com/a/10636765
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # OPTIONS 
    #+ src: https://stackoverflow.com/questions/16583827/cors-with-python-basehttpserver-501-unsupported-method-options-in-chrome
    #+ https://stackoverflow.com/a/32501309
    def do_OPTIONS(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        if ( quiet != 1):
            print("------------------------- GET -------------------------")
        self._set_headers()
            #{'hello': 'world', 'received': 'ok'}
        self.wfile.write(json.dumps(
            retrieve_json_file()
            ))
        if ( quiet != 1):
            print("you HAD one job - return the json! maybe you did? IDK")
            print("------------------------- /GET -------------------------")
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        if ( quiet != 1):
            print("------------------------- POST -------------------------")
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))

# note sure if this could conflict with the map json        
#        # add a property to the object, just to mess with data
#        message['received'] = 'ok'
        
        # send the message back - good for verification, I suppose
        self._set_headers()
        self.wfile.write(json.dumps(message))
        # store file
        save_json_file(message, "gps_input_route.json")
        if ( quiet != 1):
            print("you HAD one job - store the json! maybe you did? IDK")
            print("------------------------- /POST -------------------------")

        
def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    if ( quiet != 1):
        print(('Starting httpd on port %d...' % port))
    httpd.serve_forever()
    
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
    run_model_hook(runhook)
    # vvv intentionally fail vvv
    # qwazantch()
    # /test
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
        
