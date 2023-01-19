# mono-image containing both server and modelgen
FROM python:3.7-bullseye
# Adapted from https://github.com/docker/awesome-compose/blob/e6b1d2755f2f72a363fc346e52dce10cace846c8/flask/app/Dockerfile

# first install all python requirements
WORKDIR /app
COPY requirements.txt /app

# install requirements for modelgen; requires setup.sh to have already cloned the repo
COPY modelgen/requirements.txt modelgen/requirements.txt

# install all requirements in same layer
RUN pip3 install -r requirements.txt -r modelgen/requirements.txt

# now copy in remainder of code
COPY . /app

WORKDIR /app

CMD ["./server.py", "8009"]
ENTRYPOINT ["python3"]
