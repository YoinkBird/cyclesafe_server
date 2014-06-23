A minimal HTTP server in python. It sends a JSON Hello World for GET requests, and echoes back JSON for POST requests.

> python server.py 8009
> Starting httpd on port 8009...

> curl http://localhost:8009
> {"received": "ok", "hello": "world"}

> curl --data "{\"this\":\"is a test\"}" --header "Content-Type: application/json" http://localhost:8009
> {"this": "is a test", "received": "ok"}

Adapted from [this Gist](https://gist.github.com/bradmontgomery/2219997), with the addition of code for reading the request body taken from [this article](http://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/).