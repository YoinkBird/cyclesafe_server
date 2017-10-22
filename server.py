from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import cgi

# hard-coded globals
resource_dir = "res"
quiet = 0


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
def save_json_file(response_json, filename="gps_input_route.json"):
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
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
            #{'hello': 'world', 'received': 'ok'}
        self.wfile.write(json.dumps(
            retrieve_json_file()
            ))
        if ( quiet != 1):
            print("you HAD one job - return the json! maybe you did? IDK")
            print("-------------------------")
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
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
        save_json_file(message)
        if ( quiet != 1):
            print("you HAD one job - store the json! maybe you did? IDK")
            print("-------------------------")

        
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
    if ( quiet != 1):
        print("-------------------------")
        print("you have one job - return this string!")
        pprint.pprint(
                retrieve_json_file()
                )
        print("-------------------------")
    # test save - depends on load
    import pprint
    if ( quiet != 1):
        print("-------------------------")
        print("you have one job - save this string!")
        pprint.pprint(
                save_json_file(retrieve_json_file()) # , filename
                )
        print("-------------------------")
    # vvv intentionally fail vvv
    # qwazantch()
    # /test
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
        
