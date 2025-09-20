from functools import cache
import traceback
import requests
import zipfile
import logging
import asyncio
import logging
import socket
import time
import json
import os

from fastapi import FastAPI, BackgroundTasks, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import HTTPException
import helics as h
import uvicorn
import httpx

from oedisi.componentframework.system_configuration import (
    ComponentStruct,
    WiringDiagram,
)
from oedisi.types.common import ServerReply, HeathCheck
from oedisi.tools.broker_utils import get_time_data

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)
app = FastAPI()

WIRING_DIAGRAM_FILENAME = "system.json"
WIRING_DIAGRAM: WiringDiagram | None = None

@cache
def kubernetes_service():
    if "KUBERNETES_SERVICE_NAME" in os.environ:
        return os.environ["KUBERNETES_SERVICE_NAME"] # works with kurenetes
    elif "SERVICE_NAME" in os.environ:
        return os.environ["SERVICE_NAME"] # works with minikube
    else:
        return None

def build_url(host: str, port: int, enpoint: list):
    if kubernetes_service():
        url = f"http://{host}.{kubernetes_service()}:{port}/"
    else:
        url = f"http://{host}:{port}/"
    url = url + "/".join(enpoint) + "/"
    return url


def find_filenames(path_to_dir=os.getcwd(), suffix=".feather"):
    filenames = os.listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def read_settings():
    broker_host = socket.gethostname()
    broker_ip = socket.gethostbyname(broker_host)
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
    host_ip = socket.gethostbyname(hostname)

    response = HeathCheck(hostname=hostname, host_ip=host_ip).dict()

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
                    HTTPException(
                        400, "Invalid file type. Only zip files are accepted."
                    )

                logger.info(f"Writing profile file to disk {file.filename}")
                with open(file.filename, "wb") as f:
                    f.write(data)

                url = build_url(ip, port, ["profiles"])
                logger.info(f"Uploading profile file {file.filename} to {url}")
                files = {"file": open(file.filename, "rb")}
                r = requests.post(url, files=files)
                response = ServerReply(detail=r.text).dict()
                return JSONResponse(response, r.status_code)
        raise HTTPException(status_code=404, detail="Unable to upload profiles")
    except Exception as e:
        err = traceback.format_exc()
        raise HTTPException(status_code=500, detail=str(err))


@app.post("/sensors")
async def add_sensors(sensors: list[str]):
    try:
        component_map, _, _ = read_settings()
        for hostname in component_map:
            if "feeder" in hostname:
                ip = hostname
                port = component_map[hostname]
                url = build_url(ip, port, ["sensor"])
                logger.info(f"Uploading sensors to {url}")
                r = requests.post(url, json=sensors)
                response = ServerReply(detail=r.text).dict()
                return JSONResponse(response, r.status_code)
        raise HTTPException(status_code=404, detail="Unable to upload sensors")
    except Exception as e:
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
                    HTTPException(
                        400, "Invalid file type. Only zip files are accepted."
                    )
                logger.info(f"Writing model file to disk {file.filename}")
                with open(file.filename, "wb") as f:
                    f.write(data)

                url = build_url(ip, port, ["model"])
                logger.info(f"Uploading model file {file.filename} to {url}")
                files = {"file": open(file.filename, "rb")}
                r = requests.post(url, files=files)
                response = ServerReply(detail=r.text).dict()
                return JSONResponse(response, r.status_code)
        raise HTTPException(status_code=404, detail="Unable to upload model")
    except Exception as e:
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
            logger.info(f"Added {feather_file} to zip")

    try:
        return FileResponse(path=file_path, filename=file_path, media_type="zip")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Failed download")


@app.get("/terminate")
async def terminate_simulation():
    try:
        h.helicsCloseLibrary()
        logger.info("Closed helics library")
        return JSONResponse({"detail": "Helics broker sucessfully closed"}, 200)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Failed download ")


def _get_feeder_info(component_map: dict):
    for host in component_map:
        if host == "feeder":
            return host, component_map[host]


async def run_simulation():
    component_map, broker_ip, api_port = read_settings()
    feeder_host, feeder_port = _get_feeder_info(component_map)
    logger.info(f"{broker_ip}, {api_port}")
    initstring = f"-f {len(component_map)-1} --name=mainbroker --loglevel=trace --local_interface={broker_ip} --localport=23404"
    logger.info(f"Broker initaialization string: {initstring}")
    broker = h.helicsCreateBroker("zmq", "", initstring)

    app.state.broker = broker
    logger.info(f"Created broker: {broker}")

    isconnected = h.helicsBrokerIsConnected(broker)
    logger.info(f"Broker connected: {isconnected}")
    logger.info(str(component_map))
    broker_host = socket.gethostname()

    async with httpx.AsyncClient(timeout=None) as client:
        tasks = []
        for service_ip, service_port in component_map.items():
            if service_ip != broker_host:
                url = build_url(service_ip, service_port, ["run"])
                logger.info(f"service_ip: {service_ip}, service_port: {service_port}")
                logger.info(f"making a request to url - {url}")

                myobj = {
                    "broker_port": 23404,
                    "broker_ip": broker_ip,
                    "api_port": api_port,
                    "feeder_host": feeder_host,
                    "feeder_port": feeder_port,
                }
                logger.info(f"{myobj}")
                # create tasks so we can monitor them periodically
                task = asyncio.create_task(client.post(url[:-1], json=myobj))
                tasks.append(task)

        # Periodically log task status every 5 seconds until all done
        if tasks:
            pending = set(tasks)
            while pending:
                done = {t for t in pending if t.done()}
                for idx, t in enumerate(tasks):
                    state = (
                        "done"
                        if t.done()
                        else "cancelled"
                        if t.cancelled()
                        else "pending"
                    )
                    info = None
                    if t.done() and not t.cancelled():
                        try:
                            res = t.result()
                            info = f"status_code={getattr(res, 'status_code', 'N/A')}"
                        except Exception as exc:
                            info = f"exception={exc}"
                    logger.info(f"Task {idx}: {state} {info or ''}")

                # remove completed tasks from pending
                pending -= done

                if pending:
                    await asyncio.sleep(5)
                else:
                    # ensure exceptions are observed to avoid warnings
                    for idx, t in enumerate(tasks):
                        try:
                            res = t.result()
                            logger.info(f"Task {idx} succeeded: {getattr(res, 'status_code', 'N/A')}")
                        except Exception as exc:
                            logger.error(f"Task {idx} failed: {exc}")

    while h.helicsBrokerIsConnected(broker):
        time.sleep(1)   
        query_result = broker.query("broker", "current_state")
        logger.info(f"Federates expected: {len(component_map)-1}")
        logger.info(f"Federates connected: {len(broker.query("broker", "federates"))}")
        logger.info(f"Simulation state: {query_result['state']}")
        logger.info(f"Global time: {query_result['attributes']['parent']}")
    h.helicsCloseLibrary()

    return


@app.post("/run")
async def run_feeder(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_simulation)
        response = ServerReply(detail="Task sucessfully added.").dict()
        return JSONResponse({"detail": response}, 200)
    except Exception as e:
        err = traceback.format_exc()
        raise HTTPException(status_code=404, detail=str(err))


@app.post("/configure")
async def configure(wiring_diagram: WiringDiagram):
    global WIRING_DIAGRAM
    WIRING_DIAGRAM = wiring_diagram

    json.dump(wiring_diagram.dict(), open(WIRING_DIAGRAM_FILENAME, "w"))
    for component in wiring_diagram.components:
        component_model = ComponentStruct(component=component, links=[])
        for link in wiring_diagram.links:
            if link.target == component.name:
                component_model.links.append(link)

        url = build_url(component.host, component.container_port, ["configure"])
        logger.info(f"making a request to url - {url}")

        r = requests.post(url[:-1], json=component_model.dict())
        assert (
            r.status_code == 200
        ), f"POST request to update configuration failed for url - {url}"
    return JSONResponse(
        ServerReply(
            detail="Sucessfully updated config files for all containers"
        ).dict(),
        200,
    )


@app.get("/status")
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
    # test_function()
    # read_settings()
