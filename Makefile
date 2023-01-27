DOCKER_USER=yoinkbird
APP_NAME_SERVER=cs_server
IMAGE_TAG_SERVER=latest
IMAGE_NAME_SERVER=${DOCKER_USER}/${APP_NAME_SERVER}
URLPORT=8009
SERVER_CONTAINER_NAME=cs_server_${URLPORT}
volume_name=cs_pseudo_ipc
prepare:
	docker volume create ${volume_name}

build:
	docker build --tag ${IMAGE_NAME_SERVER} .

dev_dep:
	docker build --tag ${IMAGE_NAME_SERVER} . && \
		docker run --rm -it -v ${volume_name}:/data:rw -v ${PWD}:/app/server:rw --entrypoint bash ${IMAGE_NAME_SERVER}

dev: prepare
	docker build --tag ${IMAGE_NAME_SERVER} . && \
		docker run --rm -it -v ${volume_name}:/data:rw -v ${PWD}:/app/server:ro --entrypoint bash ${IMAGE_NAME_SERVER}


run: prepare build
	docker run -d -p ${URLPORT}:8009 -v ${volume_name}:/data:rw --name ${SERVER_CONTAINER_NAME} ${IMAGE_NAME_SERVER}

# TODO: don't depend on ./setup.sh at all
verify:
	@bash ./setup.sh verify

logs:
	docker container logs ${SERVER_CONTAINER_NAME}
exec:
	docker exec -it ${SERVER_CONTAINER_NAME} bash

data:
	docker run -it --rm -v ${volume_name}:/data:ro python:3.7-bullseye ls -l /data

kill:
	# HACK
	@docker container kill ${SERVER_CONTAINER_NAME} || true

clean: kill
	# HACK
	@docker container rm ${SERVER_CONTAINER_NAME} || true
	# HACK
	@docker volume rm ${volume_name} || true

#prune:
#	docker container rm ${SERVER_CONTAINER_NAME}
#https://docs.docker.com/engine/reference/commandline/ps/#-filtering---filter
#	docker container ls -a --filter=name=yoinkbird/cs_modelgen
#	docker container ls -a --format '{{ .Name }}' | grep ${SERVER_CONTAINER_NAME}
