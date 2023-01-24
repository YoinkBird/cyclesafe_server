# Goal

1. Containerise cyclesafe_server and modelgen,
2. Replace orchestration bash+linux setup.sh orchestration with docker fundamentals.
3. Then implement orchestration using docker-compose to (mostly) replace setup.sh.
4. Continue to implement orchestration using k8s+k3d

# Phase 1

containerize model generation



# Phase 2

containerize server setup

Simple, since server is "just" pure python server, all batteries included and no frameworks

Note: cannot mount type cache as per https://docs.docker.com/engine/reference/builder/#run---mounttypecache :
```
Step 4/10 : RUN --mount=type=cache,target=/root/.cache/pip   pip3 install -r requirements.txt
the --mount option requires BuildKit. Refer to https://docs.docker.com/go/buildkit/ to learn how to build images with BuildKit enabled
```

Note: not using Makefile as much since build management is done via setup.sh ; could convert setup.sh to Makefile though

# Phase 3

convert orchestration to use vanilla docker commands
  
  # TODO: for local dev, implement local registry and adjust variables accordingly: https://www.docker.com/blog/how-to-use-your-own-registry-2/
  # $ docker run -d -p 5000:5000 --name registry registry:latest
  # $ docker run -d -p 5000:5000 --name registry registry:latest
  # $ docker tag yoinkbird/cs_modelgen localhost:5000/yoinkbird/cs_modelgen
  # $ docker push localhost:5000/yoinkbird/cs_modelgen

## Challenge:

server.py runs model.py via the "runhook"; if both are containerised, without further changes, we would need a docker-in-docker setup to run it.

Solution:
Workaround For now, build modelgen and server in one mono-image,
work on moving the pseudo-IPC files to a volume.

Then break up the "runhook" by modifying modelgen to monitor filechanges and have the server simply touch these files instead of running the modelgen directly.

Finally, split up the mono-image into one for server, one for modelgen, as originally intended.


## mono-image

Build "mono image" as one image containing 2 repos, essentially just converting the philosophy of setup.sh to run in a container.

Modify orchestration setup.sh and Dockerfile to install dependencies needed for modelgen
* move docker build step after clone of modelgen (to copy it in)
* pip install modelgen requirements.txt

## step: prepare
For "pseudo IPC", move container build after all symlinks are created

**Caveat**:
Have to run `./setup.sh clean` to avoid:
```bash
$ ./setup.sh
ln: failed to create symbolic link 'modelgen/server/..': File exists
ln: failed to create symbolic link './res/gps_scored_route.json': File exists
```


### step: launch+kill

need ability to to launch and end server process

### PARTIAL SUCCESS

Container runs....
... and can be killed

## step: verify

### PARTIAL SUCCESS

visual verification works, updated curl options to be more strict and output to be more clear

## step: runall

./setup.sh kill
./setup.sh clean

git clean -xdf

### SUCCESS

./setup.sh

Runs, browser launches without errors from server

## Iterate, Round 2: Move hacks from setup.sh into Docker

### step: prepare, part 2

Move "pseudo IPC" into Docker, no longer using setup.sh to manage.

Break the "subdirectory" philosophy:
* [x] implement parallel hierarchy in Docker
* [x] "prepare": move link creation into Dockerfile out of setup.sh

### Verify current orchestration functionality:

I.e. what if the verification steps are insufficient, or the server is mistakenly just returning pre-configured json?

```bash
$ ./setup.sh build
$ ./setup.sh launch
# vvv empty
$ docker container logs cs_server_8009
$ ./setup.sh verify
...
$ docker container logs cs_server_8009 
./prepare_json.sh: line 5: cd: ./modelgen: No such file or directory
python3: can't open file './code/model.py': [Errno 2] No such file or directory
```

After updating `./prepare_json.sh`, the error dissapears.

**Conclusion**: The verify step is insufficient (and always was meant for manual review)

**Fix: Add Test to verify orchestration setup**:

Catch this specific error related to the runhook configuration by examining the container logs:
```
docker container logs "${server_container_name}" | grep -v "\./prepare_json.sh: line .*: cd: ./modelgen: No such file or directory"
```

Experiment to simplify the command:
```
$ bash -cxe 'echo "error" | (! grep "error"); echo "END: $?"'; echo $?
+ echo error
+ grep error
error
1
$ bash -cxe 'echo "pass" | (! grep "error"); echo "END: $?"'; echo $?
+ echo pass
+ grep error
+ echo 'END: 0'
END: 0
0

```

Note on bash return code management:
```bash
# following cmds all use 'exit immediately', i.e. '-e' to ensure that the script early-fails on first-encountered test failure or failed command (i.e. non-zero return value):
# '(exit <0|9>)' subshell is a stand-in for command being called, e.g. 'grep'
# e.g. grep has a match, returns zero, which actually means the test failed (matched error signature); the '&& false' condition ensures that the command returns non-zero after all and gets caught by 'set -e' (because it's the final && in the list)
$ bash -cxe '(exit 0) && false; echo "END: $?"'; echo $?
+ exit 0
+ false
1
# e.g. grep doesn't match, returns non-zero, which actually means the test passed (error signature not found); the presence of the '&&' operator "hides" the actual return code from 'set -e' (because 'set -e' only applies to the command of the final && in the list, which isn't run in this case)
$ bash -cxe '(exit 9) && false; echo "END: $?"'; echo $?
+ exit 9
+ echo 'END: 9'
END: 9
0

# alt: invert command return value:
# far simpler approach; found while reading manual for 'exit immediately'
# if 
# e.g. grep has a match, returns zero, which actually means the test failed (matched error signature); the precediing '!' inverts the return value to be non-zero and gets caught by 'set -e', indicating that the test failed and causing the script to halt immediately (early fail)
$ bash -cxe '! (exit 0); echo "END: $?"'; echo $?
+ exit 0
+ echo 'END: 1'
END: 1
0
# e.g. grep doesn't match, returns non-zero, which actually means the test passed (error signature not found); the preceding '!' operator inverts the return value to be zero, thus "hiding" the original non-zero value from from 'set -e', indicating that the test passed and allowing the script to continue
$ bash -cxe '! (exit 9); echo "END: $?"'; echo $?
+ exit 9
+ echo 'END: 0'
END: 0
0

```
```
-e      Exit immediately if a pipeline (which may consist of a single simple command), a list, or a compound command (see SHELL GRAMMAR above), exits with a  non-zero  sta‐
        tus.   The  shell does not exit if the command that fails is part of the command list immediately following a while or until keyword, part of the test following the
        if or elif reserved words, part of any command executed in a && or || list except the command following the final && or ||, any command in a pipeline but the  last,
        or  if the command's return value is being inverted with !.  If a compound command other than a subshell returns a non-zero status because a command failed while -e
        was being ignored, the shell does not exit.  A trap on ERR, if set, is executed before the shell exits.  This option applies to the shell environment and each  sub‐
        shell environment separately (see COMMAND EXECUTION ENVIRONMENT above), and may cause subshells to exit before executing all the commands in the subshell.

        If  a compound command or shell function executes in a context where -e is being ignored, none of the commands executed within the compound command or function body
        will be affected by the -e setting, even if -e is set and a command returns a failure status.  If a compound command or shell function sets -e while executing in  a
        context where -e is ignored, that setting will not have any effect until the compound command or the command containing the function call completes.
```
```
Examples

# demonstration of 'set -e' interaction with command following the final && or ||:

# no-exit-immediately: command fails, command following final '&&' does not get executed => original return value
$ bash -cxe '(exit 9) && (exit 1); echo "END: $?"'; echo $?
+ exit 9
+ echo 'END: 9'
END: 9
0


# exit immediately: command fails, final '||' is also failure => final return value
$ bash -cxe '(exit 9) && (exit 1) || (exit 20); echo "END: $?"'; echo $?
+ exit 9
+ exit 20
20

```

**Fix: Update test**:

Update curl-based interface tests to verify response instead of just relying on return code, since server doesn't always return appropriate HTTP error codes for internal errors.

## Iterate, Round 3: Convert Pseudo-IPC to use image dir/container volume

Goal: [ ] configure file-passing to be done via Docker volume to enable easy removal or persistence

* [x] "prepare": replace link spaghetti with a top-level dir - with a few links
* [x] comment out provisional Dockerfile symlinks

Current State of Links:
 ```bash
# Run full orchestration (build, launch, verify):
$ ./setup.sh
$ docker exec -it cs_server_8009 sh -cx 'ls -ltr /app/server/res; ls -ltr /app/modelgen/output'
+ ls -ltr /app/server/res
total 8
lrwxrwxrwx 1 root root   42 Jan 24 22:26 gps_scored_route.json -> /app/modelgen/output/gps_scored_route.json
-rw-r--r-- 1 root root 6262 Jan 24 22:26 gps_input_route.json
+ ls -ltr /app/modelgen/output
total 728
-rw-rw-r-- 1 root root 156228 Jan 23 22:40 crashes_500_1530.html
-rw-rw-r-- 1 root root  16408 Jan 23 22:40 crashes_300_330.html
-rw-rw-r-- 1 root root  99250 Jan 23 22:40 crashes_1900_500.html
-rw-rw-r-- 1 root root 111291 Jan 23 22:40 crashes_1530_1900.html
-rw-rw-r-- 1 root root 337149 Jan 23 22:40 crashes.html
lrwxrwxrwx 1 root root     36 Jan 24 22:26 gps_input_route.json -> /app/server/res/gps_input_route.json
-rw-r--r-- 1 root root   2503 Jan 24 22:27 human_read_dectree.pkl
-rw-r--r-- 1 root root    299 Jan 24 22:27 gps_scored_route.json
```

After Dockerfile update:

```bash
# clear old results
$ ./setup.sh kill
# Run full orchestration (build, launch, verify):
$ ./setup.sh
$ docker exec -it cs_server_8009 sh -cx 'ls -ltr /data; ls -ltr /app/server/res; ls -ltr /app/modelgen/output'
+ ls -ltr /data
total 736
-rw-rw-r-- 1 root root 156228 Jan 23 22:40 crashes_500_1530.html
-rw-rw-r-- 1 root root  16408 Jan 23 22:40 crashes_300_330.html
-rw-rw-r-- 1 root root  99250 Jan 23 22:40 crashes_1900_500.html
-rw-rw-r-- 1 root root 111291 Jan 23 22:40 crashes_1530_1900.html
-rw-rw-r-- 1 root root 337149 Jan 23 22:40 crashes.html
-rw-r--r-- 1 root root   6262 Jan 24 22:38 gps_input_route.json
-rw-r--r-- 1 root root   2503 Jan 24 22:38 human_read_dectree.pkl
-rw-r--r-- 1 root root    298 Jan 24 22:38 gps_scored_route.json
+ ls -ltr /app/server/res
lrwxrwxrwx 1 root root 5 Jan 24 22:38 /app/server/res -> /data
+ ls -ltr /app/modelgen/output
lrwxrwxrwx 1 root root 5 Jan 24 22:38 /app/modelgen/output -> /data
```
Looks good:
* .html files show up
* server/res generated gps_input_route.json is present
* model/output generated gps_scored_route.json is present, as is the pickled model human_read_dectree.pkl

* [ ] containerise: convert the orchestration steps to use docker volume: https://docs.docker.com/storage/volumes/
* [x] clean+reset
* [ ] prepare 

Verify:

```bash
$ docker volume inspect cs_pseudo_ipc 
[
    {
        "CreatedAt": "2023-01-24T17:24:57-06:00",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/cs_pseudo_ipc/_data",
        "Name": "cs_pseudo_ipc",
        "Options": {},
        "Scope": "local"
    }
]
$ sudo ls -ltr /var/lib/docker/volumes/cs_pseudo_ipc/_data
total 736
-rw-rw-r-- 1 root root 337149 Jan 23 16:40 crashes.html
-rw-rw-r-- 1 root root 156228 Jan 23 16:40 crashes_500_1530.html
-rw-rw-r-- 1 root root  16408 Jan 23 16:40 crashes_300_330.html
-rw-rw-r-- 1 root root  99250 Jan 23 16:40 crashes_1900_500.html
-rw-rw-r-- 1 root root 111291 Jan 23 16:40 crashes_1530_1900.html
-rw-r--r-- 1 root root   6262 Jan 24 17:24 gps_input_route.json
-rw-r--r-- 1 root root   2503 Jan 24 17:24 human_read_dectree.pkl
-rw-r--r-- 1 root root    299 Jan 24 17:24 gps_scored_route.json
```

Niiiceee


# Phase 4

convert orchestration to docker-compose, for now.


# ISSUES

update server response for POST; server POST response shouldn't return the full json body, only a 200: https://github.com/YoinkBird/cyclesafe_server/issues/20
server GET should propagate errors from the runhook: https://github.com/YoinkBird/cyclesafe_server/issues/22
create dedicated model test; replace steps within verify step with a standalone test, either in the model repo, or in the server repo (if for some reason the input/output depends on the server): https://github.com/YoinkBird/cyclesafe_server/issues/23


server should propagate error on invalid GET: https://github.com/YoinkBird/cyclesafe_server/issues/24
```
Traceback (most recent call last):
  File "./code/model.py", line 1585, in <module>
    score_manual_generic_route(data, data_dummies, df_int_nonan, featdef, **options_local)
  File "./code/model.py", line 1320, in score_manual_generic_route
    geodata = mock_receive_request_json(**options)
  File "./code/model.py", line 582, in mock_receive_request_json
    return retrieve_json_file(filepath, **options)
  File "./code/model.py", line 548, in retrieve_json_file
    with open(filepath, 'r') as infile:
FileNotFoundError: [Errno 2] No such file or directory: 'output/gps_input_route.json'

```


convert curl tests to fail on http errors; convert curl tests to use `--fail` or `--fail-with-body` (both meant for server errors/HTTP codes), not `--fail-early` (meant for transmission errors): https://github.com/YoinkBird/cyclesafe_server/issues/25
```
--fail
(HTTP) Fail silently (no output at all) on server errors. 
```

note also
```
       -i, --include
              Include the HTTP response headers in the output. The HTTP response headers can include things like server name, cookies, date of the document, HTTP version and more...

              To view the request headers, consider the -v, --verbose option.

              Example:
               curl -i https://example.com

              See also -v, --verbose.

```
