FROM python:3.10.6-slim-bullseye

RUN apt-get update
RUN apt-get install -y git ssh

RUN mkdir player
COPY . ./player
WORKDIR ./player

RUN pip install -e .

EXPOSE 5680/tcp

CMD ["python", "-m", "player.server"]
