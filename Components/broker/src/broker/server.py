import json
import logging
import os
import socket
import time
import traceback
import zipfile

import grequests
import helics as h
import requests
import uvicorn
from fastapi import BackgroundTasks, FastAPI, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, JSONResponse
from oedisi.componentframework.system_configuration import (
    ComponentStruct,
    WiringDiagram,
)
from oedisi.tools.broker_utils import get_time_data
from oedisi.types.common import HeathCheck, ServerReply

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

is_kubernetes_env = (
    os.environ["KUBERNETES_SERVICE_NAME"] if "KUBERNETES_SERVICE_NAME" in os.environ else None
)

WIRING_DIAGRAM_FILENAME = "system.json"
WIRING_DIAGRAM: WiringDiagram | None = None


def build_url(host: str, port: int, enpoint: list):
    if is_kubernetes_env:
        KUBERNETES_SERVICE_NAME = os.environ["KUBERNETES_SERVICE_NAME"]
        url = f"http://{host}.{KUBERNETES_SERVICE_NAME}:{port}/"
    else:
        url = f"http://{host}:{port}/"
    url = url + "/".join(enpoint) + "/"
    return url


def find_filenames(path_to_dir=os.getcwd(), suffix=".feather"):
    filenames = os.listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def read_settings():
    broker_host = socket.gethostname()
    try:
        broker_ip = socket.gethostbyname(broker_host)
    except socket.gaierror:
        broker_ip = "127.0.0.1"
    api_port = 8766  # int(os.environ['PORT'])

    component_map = {broker_host: api_port}
    if WIRING_DIAGRAM:
        for component in WIRING_DIAGRAM.components:
            component_map[component.host] = component.container_port
    else:
        logger.info(
            "Use the '/configure' setpoint to setup up the WiringDiagram before making requests other enpoints"
        )

    return component_map, broker_ip, api_port


@app.get("/")
def read_root():
    hostname = socket.gethostname()
    try:
        host_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        host_ip = "127.0.0.1"

    response = HeathCheck(hostname=hostname, host_ip=host_ip).model_dump()

    return JSONResponse(response, 200)


@app.post("/profiles")
async def upload_profiles(file: UploadFile):
    try:
        component_map, _, _ = read_settings()
        for hostname in component_map:
            if "feeder" in hostname:
                ip = hostname
                port = component_map[hostname]
                data = file.file.read()
                if not file.filename.endswith(".zip"):
                    HTTPException(400, "Invalid file type. Only zip files are accepted.")
                with open(file.filename, "wb") as f:
                    f.write(data)

                url = build_url(ip, port, ["profiles"])
                logger.info(f"making a request to url - {url}")

                files = {"file": open(file.filename, "rb")}
                r = requests.post(url, files=files)
                response = ServerReply(detail=r.text).model_dump()
                return JSONResponse(response, r.status_code)
        raise HTTPException(status_code=404, detail="Unable to upload profiles")
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(status_code=500, detail=str(err))


@app.post("/model")
async def upload_model(file: UploadFile):
    try:
        component_map, _, _ = read_settings()
        for hostname in component_map:
            if "feeder" in hostname:
                ip = hostname
                port = component_map[hostname]
                data = file.file.read()
                if not file.filename.endswith(".zip"):
                    HTTPException(400, "Invalid file type. Only zip files are accepted.")
                with open(file.filename, "wb") as f:
                    f.write(data)

                url = build_url(ip, port, ["model"])
                logger.info(f"making a request to url - {url}")

                files = {"file": open(file.filename, "rb")}
                r = requests.post(url, files=files)
                response = ServerReply(detail=r.text).model_dump()
                return JSONResponse(response, r.status_code)
        raise HTTPException(status_code=404, detail="Unable to upload model")
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(status_code=500, detail=str(err))


@app.get("/results")
def download_results():
    component_map, _, _ = read_settings()

    for hostname in component_map:
        if "recorder" in hostname:
            host = hostname
            port = component_map[hostname]

            url = build_url(host, port, ["download"])
            logger.info(f"making a request to url - {url}")

            response = requests.get(url)
            logger.info(f"Response from {hostname} has {len(response.content)} bytes")
            with open(f"{hostname}.feather", "wb") as out_file:
                out_file.write(response.content)

    file_path = "results.zip"
    with zipfile.ZipFile(file_path, "w") as zipMe:
        for feather_file in find_filenames():
            zipMe.write(feather_file, compress_type=zipfile.ZIP_DEFLATED)

    try:
        return FileResponse(path=file_path, filename=file_path, media_type="zip")
    except Exception:
        raise HTTPException(status_code=404, detail="Failed download")


@app.get("/terminate")
def terminate_simulation():
    try:
        h.helicsCloseLibrary()
        return JSONResponse({"detail": "Helics broker sucessfully closed"}, 200)
    except Exception:
        raise HTTPException(status_code=404, detail="Failed download ")


def _get_feeder_info(component_map: dict):
    for host in component_map:
        if host == "feeder":
            return host, component_map[host]


def run_simulation():
    component_map, broker_ip, api_port = read_settings()
    feeder_host, feeder_port = _get_feeder_info(component_map)
    logger.info(f"{broker_ip}, {api_port}")
    initstring = f"-f {len(component_map)-1} --name=mainbroker --loglevel=trace --local_interface={broker_ip} --localport=23404"
    logger.info(f"Broker initaialization string: {initstring}")
    broker = h.helicsCreateBroker("zmq", "", initstring)

    app.state.broker = broker
    logging.info(broker)

    isconnected = h.helicsBrokerIsConnected(broker)
    logger.info(f"Broker connected: {isconnected}")
    logger.info(str(component_map))
    replies = []

    broker_host = socket.gethostname()

    for service_ip, service_port in component_map.items():
        if service_ip != broker_host:
            url = build_url(service_ip, service_port, ["run"])
            logger.info(f"making a request to url - {url}")

            myobj = {
                "broker_port": 23404,
                "broker_ip": broker_ip,
                "api_port": api_port,
                "feeder_host": feeder_host,
                "feeder_port": feeder_port,
            }
            replies.append(grequests.post(url, json=myobj))
    grequests.map(replies)
    while h.helicsBrokerIsConnected(broker):
        time.sleep(1)
    h.helicsCloseLibrary()

    return


@app.post("/run")
async def run_feeder(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_simulation)
        response = ServerReply(detail="Task sucessfully added.").model_dump()
        return JSONResponse({"detail": response}, 200)
    except Exception:
        err = traceback.format_exc()
        raise HTTPException(status_code=404, detail=str(err))


@app.post("/configure")
async def configure(wiring_diagram: WiringDiagram):
    global WIRING_DIAGRAM
    WIRING_DIAGRAM = wiring_diagram

    json.dump(wiring_diagram.model_dump(), open(WIRING_DIAGRAM_FILENAME, "w"))
    for component in wiring_diagram.components:
        component_model = ComponentStruct(component=component, links=[])
        for link in wiring_diagram.links:
            if link.target == component.name:
                component_model.links.append(link)

        url = build_url(component.host, component.container_port, ["configure"])
        logger.info(f"making a request to url - {url}")

        r = requests.post(url, json=component_model.model_dump())
        assert r.status_code == 200, f"POST request to update configuration failed for url - {url}"
    return JSONResponse(
        ServerReply(detail="Sucessfully updated config files for all containers").model_dump(),
        200,
    )


@app.get("/status/")
async def status():
    try:
        name_2_timedata = {}
        connected = h.helicsBrokerIsConnected(app.state.broker)
        if connected:
            for time_data in get_time_data(app.state.broker):
                if (time_data.name not in name_2_timedata) or (
                    name_2_timedata[time_data.name] != time_data
                ):
                    name_2_timedata[time_data.name] = time_data
        return {"connected": connected, "timedata": name_2_timedata, "error": False}
    except AttributeError as e:
        return {"reply": str(e), "error": True}


def main():
    """Entry point for broker-server console script."""
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8766")))


if __name__ == "__main__":
    main()
