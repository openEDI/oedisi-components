FROM python:3.10.6-slim-bullseye

RUN apt-get update
RUN apt-get install -y git ssh

RUN mkdir omoo_federate
COPY . ./omoo_federate
WORKDIR ./omoo_federate

RUN pip install -e .

EXPOSE 5685/tcp

CMD ["python", "-m", "omoo_federate.server"]
