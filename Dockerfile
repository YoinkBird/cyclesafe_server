FROM python:3.7-bullseye
# Adapted from https://github.com/docker/awesome-compose/blob/e6b1d2755f2f72a363fc346e52dce10cace846c8/flask/app/Dockerfile

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app

