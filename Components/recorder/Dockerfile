FROM python:3.10.6-slim-bullseye

RUN apt-get update
RUN apt-get install -y git ssh

RUN mkdir recorder
COPY . ./recorder
WORKDIR ./recorder

RUN pip install -e .

EXPOSE 5679/tcp

CMD ["python", "-m", "recorder.server"]
