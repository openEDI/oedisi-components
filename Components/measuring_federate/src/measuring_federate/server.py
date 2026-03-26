import json
import logging
import os
import socket
import traceback

import requests
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from oedisi.componentframework.system_configuration import ComponentStruct
from oedisi.types.common import BrokerConfig, DefaultFileNames, HeathCheck, ServerReply

from .measuring_federate import run_simulator

app = FastAPI()

is_kubernetes_env = os.environ["SERVICE_NAME"] if "SERVICE_NAME" in os.environ else None


def build_url(host: str, port: int, enpoint: list):
    if is_kubernetes_env:
        SERVICE_NAME = os.environ["SERVICE_NAME"]
        url = f"http://{host}.{SERVICE_NAME}:{port}/"
    else:
        url = f"http://{host}:{port}/"
    url = url + "/".join(enpoint)
    return url


@app.get("/")
async def read_root():
    hostname = socket.gethostname()
    try:
        host_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        host_ip = "127.0.0.1"
    response = HeathCheck(hostname=hostname, host_ip=host_ip).model_dump()
    return JSONResponse(response, 200)


@app.post("/run")
async def run_model(broker_config: BrokerConfig, background_tasks: BackgroundTasks):
    logging.info(broker_config)
    feeder_host = broker_config.feeder_host
    feeder_port = broker_config.feeder_port
    url = build_url(feeder_host, feeder_port, ["sensor"])
    logging.info(url)
    try:
        reply = requests.get(url)
        sensor_data = reply.json()
        if not sensor_data:
            msg = "empty sensor list"
            raise HTTPException(404, msg)
        logging.info(sensor_data)
        with open("sensors.json", "w") as outfile:
            json.dump(sensor_data, outfile)

        background_tasks.add_task(run_simulator, broker_config)
        response = ServerReply(detail="Task sucessfully added.").model_dump()
        return JSONResponse(response, 200)
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(500, str(err))


@app.post("/configure")
async def configure(component_struct: ComponentStruct):
    component = component_struct.component
    params = component.parameters
    params["name"] = component.name
    links = {}
    for link in component_struct.links:
        links[link.target_port] = f"{link.source}/{link.source_port}"
    json.dump(links, open(DefaultFileNames.INPUT_MAPPING.value, "w"))
    json.dump(params, open(DefaultFileNames.STATIC_INPUTS.value, "w"))
    response = ServerReply(detail="Sucessfully updated configuration files.").model_dump()
    return JSONResponse(response, 200)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))


def main():
    """Entry point for measuring-federate-server console script."""
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5684")))
