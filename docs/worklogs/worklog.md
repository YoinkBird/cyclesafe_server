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

Note: cannot mount type cache as per https://docs.docker.com/engine/reference/builder/#run---mounttypecache :
```
Step 4/10 : RUN --mount=type=cache,target=/root/.cache/pip   pip3 install -r requirements.txt
the --mount option requires BuildKit. Refer to https://docs.docker.com/go/buildkit/ to learn how to build images with BuildKit enabled
```

Note: not using Makefile as much since build management is done via setup.sh ; could convert setup.sh to Makefile though

# Phase 3

convert orchestration to use vanilla docker commands
  

# Phase 4

convert orchestration to docker-compose, for now.


