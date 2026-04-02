FROM python:3.11.10

WORKDIR /simulation

COPY scenarios/docker_system.json docker_system.json
COPY components.json .
COPY Components Components
COPY README.md .

RUN mkdir -p outputs build

RUN pip install -e Components/broker \
				-e Components/lindistflow_federate \
				-e Components/LocalFeeder \
				-e Components/measuring_federate \
				-e Components/recorder \
				-e Components/wls_federate

RUN oedisi build --system docker_system.json
ENTRYPOINT ["oedisi", "run"]
