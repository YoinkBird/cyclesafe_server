# Goal

1. Containerise cyclesafe_server and modelgen,
2. Replace orchestration bash+linux setup.sh orchestration with 
3. docker fundamentals.
4. Then implement orchestration using docker-compose to (mostly) replace setup.sh.
5. Continue to implement orchestration using k8s+k3d

# Phase 1

containerize model generation



# Phase 2

containerize server setup

Simple, since server is "just" pure python server, all batteries included and no frameworks

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

# FUTURE:

```bash
# TODO: containerise: convert the steps for clean,reset,prepare to use docker volume: https://docs.docker.com/storage/volumes/
# remove the generated files and links

# TODO: container_volume_name="cs_pseudo_ipc"
# TODO: $dbecho docker volume rm "${container_volume_name}"
```

# FUTURE:

[x] Optimise Docker layer caching for python pip

# Phase 4

convert orchestration to docker-compose, for now.


