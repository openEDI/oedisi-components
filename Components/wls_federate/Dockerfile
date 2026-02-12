FROM python:3.10.6-slim-bullseye

RUN apt-get update
RUN apt-get install -y git ssh

RUN mkdir wls_federate
COPY . ./wls_federate
WORKDIR ./wls_federate

RUN pip install -e .

EXPOSE 5683/tcp

CMD ["python", "-m", "wls_federate.server"]
