A minimal HTTP server in python. It sends a JSON Hello World for GET requests, and echoes back JSON for POST requests.

```
python server.py 8009
Starting httpd on port 8009...
```

```
curl http://localhost:8009
{"received": "ok", "hello": "world"}
```

```
curl --data "{\"this\":\"is a test\"}" --header "Content-Type: application/json" http://localhost:8009
{"this": "is a test", "received": "ok"}
```

Adapted from [this Gist](https://gist.github.com/bradmontgomery/2219997), with the addition of code for reading the request body taken from [this article](http://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/).

Please be careful when using a server like this on production environments, because it lacks many important features (threading to name one). You can consult [the python documentation about BaseHTTPServer](https://docs.python.org/2/library/basehttpserver.html) to learn something useful to improve it.

If you are on Ubuntu, you can install this code as a service with an init script (hopefully, with some modifications that make it actually do something useful). Just modify the include `server.conf` to suit your needs (possibly renaming it and redirecting output to some log files instead of `/dev/null`), and copy it into `/etc/init/`. You can then start/stop/restart the server with the usual `service` command:

```
sudo service server start
```