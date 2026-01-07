FROM python:3.10.6-slim-bullseye
LABEL org.opencontainers.image.authors="Aadil Latif <aadil.latif@nrel.gov>"
RUN apt-get update
RUN apt-get install -y git ssh
RUN apt install build-essential cmake git python3-dev -y
RUN mkdir LocalFeeder
COPY  . ./LocalFeeder
WORKDIR ./LocalFeeder
RUN pip install -r requirements.txt
EXPOSE 5678/tcp
CMD ["python", "server.py"]
