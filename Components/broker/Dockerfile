FROM python:3.10.6-slim-bullseye

RUN apt-get update 
RUN apt-get install -y git ssh

RUN mkdir broker
COPY . ./broker
WORKDIR ./broker

RUN pip install -e .

EXPOSE 8766/tcp

CMD ["python", "-m", "broker.server"]
