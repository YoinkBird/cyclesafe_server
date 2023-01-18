FROM python:3.7-bullseye
#FROM python:3.8-buster
#FROM python:3.10-buster

WORKDIR /src
COPY . .

RUN test -e requirements.txt && pip3 install -r requirements.txt || echo "no requirements.txt found"

CMD ["./server.py", "8009"]
ENTRYPOINT ["python3"]
