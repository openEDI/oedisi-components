FROM python:3.13-slim-bullseye

RUN apt-get update 
RUN apt-get install -y git ssh
RUN apt install build-essential cmake git python3-dev -y


RUN mkdir broker
COPY  * ./broker
WORKDIR ./broker

RUN pip install -r requirements.txt

EXPOSE 8766/tcp

CMD ["python", "server.py"]
