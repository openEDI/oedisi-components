FROM python:3.10.6-slim-bullseye
RUN apt-get update
RUN apt-get install -y git ssh
RUN apt install build-essential cmake git python3-dev -y
RUN mkdir Recorder
COPY  . ./Recorder
WORKDIR ./Recorder
RUN pip install -r requirements.txt
EXPOSE 5679/tcp
CMD ["python", "server.py"]
