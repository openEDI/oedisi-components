"""Player server for OEDISI co-simulation dataset playback."""

import json
import logging
import os
import socket

import uvicorn
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from oedisi.componentframework.system_configuration import ComponentStruct
from oedisi.types.common import BrokerConfig, DefaultFileNames, HeathCheck, ServerReply

from .play_dataset import run_simulator

app = FastAPI()


@app.get("/")
def read_root():
    """Health check endpoint."""
    hostname = socket.gethostname()
    try:
        host_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        host_ip = "127.0.0.1"

    response = HeathCheck(hostname=hostname, host_ip=host_ip).model_dump()
    return JSONResponse(response, 200)


@app.post("/run")
async def run_model(broker_config: BrokerConfig, background_tasks: BackgroundTasks):
    """Start the player simulation in a background task."""
    logging.info(broker_config)
    background_tasks.add_task(run_simulator, broker_config)
    response = ServerReply(detail="Task successfully added.").model_dump()
    return JSONResponse(response, 200)


@app.post("/configure")
async def configure(component_struct: ComponentStruct):
    """Configure the player component."""
    component = component_struct.component
    params = component.parameters
    params["name"] = component.name
    # Player has no dynamic inputs, but we write an empty input_mapping for framework compatibility
    links = {}
    for link in component_struct.links:
        links[link.target_port] = f"{link.source}/{link.source_port}"
    with open(DefaultFileNames.INPUT_MAPPING.value, "w") as f:
        json.dump(links, f)
    with open(DefaultFileNames.STATIC_INPUTS.value, "w") as f:
        json.dump(params, f)
    response = ServerReply(detail="Successfully updated configuration files.").model_dump()
    return JSONResponse(response, 200)


def main():
    """Entry point for player-server console script."""
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5680")))


if __name__ == "__main__":
    main()
