# mono-image containing both server and modelgen
FROM python:3.7-bullseye
#FROM python:3.8-buster
#FROM python:3.10-buster

WORKDIR /src
COPY . .

RUN test -e requirements.txt && pip3 install -r requirements.txt || echo "no requirements.txt found"

# install requirements for modelgen; requires setup.sh to have already cloned the repo
WORKDIR /src/modelgen
RUN test -e requirements.txt && pip3 install -r requirements.txt || echo "no requirements.txt found"

WORKDIR /src

CMD ["./server.py", "8009"]
ENTRYPOINT ["python3"]
