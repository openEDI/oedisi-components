FROM python:3.10.6-slim-bullseye

RUN apt-get update 
RUN apt-get install -y git ssh

RUN mkdir lindistflow_federate
COPY . ./lindistflow_federate
WORKDIR ./lindistflow_federate

RUN pip install -e .

EXPOSE 5000/tcp

CMD ["python", "-m", "lindistflow_federate.server"]
