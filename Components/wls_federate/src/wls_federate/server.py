"""Server for WLS state estimator federate."""

import json
import os
import socket

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from oedisi.componentframework.system_configuration import ComponentStruct
from oedisi.types.common import BrokerConfig, DefaultFileNames, HeathCheck, ServerReply

from .state_estimator_federate import run_simulator

app = FastAPI()


@app.get("/")
def read_root():
    """Health check endpoint."""
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    response = HeathCheck(hostname=hostname, host_ip=host_ip).model_dump()
    return JSONResponse(response, 200)


@app.post("/run")
async def run_model(broker_config: BrokerConfig, background_tasks: BackgroundTasks):
    """Run the federate model."""
    print(broker_config)
    try:
        background_tasks.add_task(run_simulator, broker_config)
        response = ServerReply(detail="Task sucessfully added.").model_dump()
        return JSONResponse(response, 200)
    except Exception as err:
        raise HTTPException(500, str(err)) from err


@app.post("/configure")
async def configure(component_struct: ComponentStruct):
    """Configure the federate."""
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


def main():
    """Entry point for wls-federate-server console script."""
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "5683")))


if __name__ == "__main__":
    main()
