from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import cgi

# hard-coded globals
resource_dir = "res"
quiet = 1


# dump json to file for consumption by whatever else needs it
def retrieve_json_file(filename="gps_scored_route.json"):
    if ( quiet != 1):
        print("# save to file")
    # tmp:
    filepath=("%s/%s" % (resource_dir, filename))
    if ( quiet != 1):
        print("mock-response sending to : " + filepath)
    # with open(filepath, 'w') as outfile:
    #    json.dump(response_json, outfile)

    # verify
    loadedjson = str()
    with open(filepath, 'r') as infile:
       loadedjson = json.load(infile)

    loadedroute = json.loads(loadedjson)

    return_value = -1
    # verify
    # if( response_json == loadedjson ):
    #     print("json string resurrected successfully")
    #     return_value = 1
    # compare the dict if possible?

    # return json string
    return loadedjson

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
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message))

        
def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    if ( quiet != 1):
        print(('Starting httpd on port %d...' % port))
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv
    
    # test
    import pprint
    if ( quiet != 1):
        print("-------------------------")
        print("you have one job - return this string!")
        pprint.pprint(
                retrieve_json_file()
                )
        print("-------------------------")
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
        
