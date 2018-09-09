from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import socketserver
import json
import cgi
import re
import shutil
import os.path

import server_api_model
'''
Documentation: see setup.sh
'''

# hard-coded globals
# vvv duplicated in server_api_model
quiet = 0
# vvv used in "main", duplicated in server_api_model
selftest = 0

# kv of keys and file-paths
#+ for now, just one filepath
#key_generated_static = int()
key_generated_static = 100001
keystore = {}

class Server(BaseHTTPRequestHandler):
    def _set_headers_common(self):
        self.send_response(200)
        # TODO: Allow-Origin has to be a domain-name in prod!
        #+ src: https://stackoverflow.com/a/10636765
#        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def _set_headers_json(self):
        self._set_headers_common()
        self.send_header('Content-type', 'application/json')
    def _set_headers_html(self):
        self._set_headers_common()
        self.send_header('Content-type', 'text/html')

    # handlers
    def do_HEAD(self):
        self._set_headers_json()
        self.end_headers()
        
    # OPTIONS 
    #+ src: https://stackoverflow.com/questions/16583827/cors-with-python-basehttpserver-501-unsupported-method-options-in-chrome
    #+ https://stackoverflow.com/a/32501309
    def do_OPTIONS(self):
        self._set_headers_json()
        self.end_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        if ( quiet != 1):
            print("------------------------- GET -------------------------")
            #stub for test-response# {'hello': 'world', 'received': 'ok'}
        # determine path
        # src: https://docs.python.org/2/library/urlparse.html
        # clue via src: https://stackoverflow.com/questions/33662842/simple-python-server-to-process-get-and-post-requests-with-json
        parsed_path = urllib.parse.urlparse(self.path)
        print( "self path:" + self.path )
        print( "PARSED PATH: ")
        print( parsed_path )
        pattern = re.compile( '/(.*)' )
        matches = pattern.match( self.path )
        if ( re.match("/rest/.*", parsed_path.path) ):
            self._set_headers_json()
            self.end_headers()
            if ( parsed_path.path == "/rest/score/retrieve" ):
                if(0):
                    print("----------------------\nkeystore\n-----------------")
                    print(type(key_generated_static) )
                    print(json.dumps( (key_generated_static , keystore) ))
                    print("----------------------\nkeystore\n-----------------")
                # TODO: store data directly in: keystore[key_generated_static])
                self.wfile.write(json.dumps(
                    server_api_model.retrieve_json_results( key_generated_static )
                    ).encode())
            if ( quiet != 1):
                print("you HAD one job - return the json! maybe you did? IDK")
        # TODO: check otherwise, matches will always be defined
        #+ Group 0 is always present; it's the whole RE, so match object methods all have group 0 as their default argument.
        #+ src: https://docs.python.org/2/howto/regex.html#grouping
        #+ note: copy-paste included "non-ascii" byte, identified with vim search '/[^\x00-\x7F]' via https://stackoverflow.com/a/16987522
        elif ( matches  ):
            print("searching for normal html page")
            filepath = matches.group(1)
            print("requested: " + filepath)
            if(filepath == ""):
                filepath = "directions.html"
            # path exists - src: https://stackoverflow.com/a/82852
            if( os.path.isfile(filepath) ):
              print("found normal html page: " + filepath)
              self._set_headers_html()
              self.end_headers()
              # src: https://stackoverflow.com/a/45152020
              with open( filepath) as file:
                self.wfile.write( file.read().encode() )
        if ( quiet != 1):
            print("------------------------- /GET -------------------------")
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        if ( quiet != 1):
            print("------------------------- POST -------------------------")
        # determine path
        # src: https://docs.python.org/2/library/urlparse.html
        # clue via src: https://stackoverflow.com/questions/33662842/simple-python-server-to-process-get-and-post-requests-with-json
        parsed_path = urllib.parse.urlparse(self.path)
        print( "PARSED PATH: ")
        print( parsed_path )

        # only allow this one rest api path for now
        if ( parsed_path.path != "/rest/score/upload" ):
            self.send_response(400)
            self.end_headers()
            return

        # prepare headers
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        #+ src: https://stackoverflow.com/a/2124520
        length = int(self.headers['content-length'])
        message = json.loads(self.rfile.read(length))

        # send the message back - good for verification, I suppose
        self._set_headers_json()
        self.end_headers()
        self.wfile.write(json.dumps(message).encode())
        # store file
        #+ TODO: implement keys, but for now: static key, i.e. only one possible. will get messy for multiple requests
        key_generated, filepath_generated = server_api_model.save_json_file(message, "gps_input_route.json", 100001)
        key_generated_static = key_generated
        # TODO: store message directly for future retrieval message
        #+ keystore[key_generated_static] = message
        #+ then modify accordingly:
        #+ server_api_model.retrieve_json_results( data = keystore[key_generated_static])
        #+ 
        keystore[key_generated_static] = filepath_generated
        if(0):
            print("----------------------\nkeystore\n-----------------")
            print(type(key_generated_static) )
            print(json.dumps( (key_generated_static , keystore) ))
            print("----------------------\nkeystore\n-----------------")
        if ( quiet != 1):
            print("you HAD one job - store the json! maybe you did? IDK")
            print("------------------------- /POST -------------------------")

        
def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    if ( quiet != 1):
        print(('Starting httpd on port %d...' % port))
    # self-terminate the port on KeyboardInterrupt
    # src: https://gist.github.com/tliron/8e9757180506f25e46d9#file-rest-py-L177
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    
if __name__ == "__main__":
    from sys import argv
    
    if ( selftest == 0):
        if len(argv) == 2:
            run(port=int(argv[1]))
        else:
            run()
        


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


