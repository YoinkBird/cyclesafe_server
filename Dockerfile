# mono-image containing both server and modelgen
FROM python:3.7-bullseye
# Adapted from https://github.com/docker/awesome-compose/blob/e6b1d2755f2f72a363fc346e52dce10cace846c8/flask/app/Dockerfile

WORKDIR /app
# first install all python requirements
COPY requirements.txt /app/server/requirements.txt

# install requirements for modelgen; requires setup.sh to have already cloned the repo
COPY modelgen/requirements.txt /modules/modelgen/requirements.txt

# install all requirements in same layer
RUN pip3 install -r /app/server/requirements.txt -r /modules/modelgen/requirements.txt

# now copy in remainder of code
COPY . /app/server
# super stupid hack to get modelgen to correct place; don't want to `mv` to avoid messing with the requirements.txt
RUN rm -rf /app/server/modelgen
COPY modelgen /modules/modelgen
#RUN rm -rf /app/modelgen/ && mv /app/

# data storage
WORKDIR /data
# configure pseudo-IPC data-passing directories via symlinks
# ./res/    : server reads/writes here
# ./output/ : model  reads/writes here
# hack - run ... bash to get shopt to move the contents. verify later whether this is necessary, and for now just make whatever changes necessary to dockerfile
RUN /bin/bash -c 'shopt -s dotglob; mv /modules/modelgen/output/* /data/ && rm -rf /modules/modelgen/output'
RUN ln -vs /data /modules/modelgen/output
# hack - this dir exists, but needs to be a link
RUN rm -r /app/server/res && ln -vs /data /app/server/res
WORKDIR /app/server
# hack - enabling modules import for modelgen from parallel dir
ENV PYTHONPATH=${PYTHONPATH:+${PYTHONPATH}:}/modules

CMD ["./server.py", "8009"]
ENTRYPOINT ["python3"]
