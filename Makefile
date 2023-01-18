DOCKER_USER=yoinkbird
TAG=${DOCKER_USER}/cs_server
dev_dep:
	docker build --tag ${TAG} . && \
		docker run --rm -it -v ${PWD}:/src:rw --entrypoint bash ${TAG}
# omitting; using already existing setup.sh instead
#build:
#	docker build --tag ${TAG} .
#
#run:
#	docker run ${TAG}
