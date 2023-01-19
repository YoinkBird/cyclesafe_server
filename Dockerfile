# mono-image containing both server and modelgen
FROM python:3.7-bullseye
#FROM python:3.8-buster
#FROM python:3.10-buster

WORKDIR /src
#COPY requirements.txt requirements.txt

# RUN test -e requirements.txt && pip3 install -r requirements.txt || echo "no requirements.txt found"


# install requirements for modelgen; requires setup.sh to have already cloned the repo
WORKDIR /src/modelgen
COPY modelgen/requirements.txt requirements.txt
RUN test -e requirements.txt && pip3 install -r requirements.txt || echo "no requirements.txt found"

WORKDIR /src

COPY . .

CMD ["./server.py", "8009"]
ENTRYPOINT ["python3"]
