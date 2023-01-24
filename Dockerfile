# mono-image containing both server and modelgen
FROM python:3.7-bullseye
# Adapted from https://github.com/docker/awesome-compose/blob/e6b1d2755f2f72a363fc346e52dce10cace846c8/flask/app/Dockerfile

WORKDIR /app
# first install all python requirements
COPY requirements.txt /app/server/requirements.txt

# install requirements for modelgen; requires setup.sh to have already cloned the repo
COPY modelgen/requirements.txt /app/modelgen/requirements.txt

# install all requirements in same layer
RUN pip3 install -r /app/server/requirements.txt -r /app/modelgen/requirements.txt

# now copy in remainder of code
COPY . /app/server
# super stupid hack to get modelgen to correct place; don't want to `mv` to avoid messing with the requirements.txt
RUN rm -rf /app/server/modelgen
COPY modelgen /app/modelgen
#RUN rm -rf /app/modelgen/ && mv /app/

# setup pseudo-IPC via symlinks, files, and directories
# ./res/    : server reads/writes here
# ./output/ : model  reads/writes here
# NOTE: not optimising these RUN commands at all because they should be temporary!
# single entry point from model to server, i.e. links go through <modeldir>/server
RUN ln -v -s /app/server /app/modelgen/server
## files from model:
### output from server to model : the map json route received from web
RUN ln -f -v -s /app/server/res/gps_input_route.json /app/modelgen/output/gps_input_route.json
### input to server from model : the scored json route scored by the model
RUN ln -v -s /app/modelgen/output/gps_scored_route.json /app/server/res/gps_scored_route.json 

WORKDIR /app/server

CMD ["./server.py", "8009"]
ENTRYPOINT ["python3"]
