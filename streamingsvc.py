"""
server.py
This script will launch a web server on port 8000 which sends SSE events anytime
logs are added to our log file.
"""
import json
import time
import aioredis
from typing import List, Tuple, Dict
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
import uvicorn
from sh import tail
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from subprocess import Popen, PIPE, CalledProcessError
# create our app instance
app = FastAPI()

# add CORS so our web page can connect to our api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)
LOGFILE = f"{dir_path}/test.log"

# SLEEP_INTERVAL = 0.5
# redis = await aioredis.create_redis("redis://127.0.0.1:6379")
# Message = Tuple[bytes, bytes, Dict[bytes, bytes]]


async def clear_stream(
        redis: aioredis.Redis, stream: str):
    print('Clearing stream - ', stream)
    await redis.xtrim(stream, 0)


async def write_to_stream(
        redis: aioredis.Redis, stream: str, commandstr: str):
    print('Writing to stream - ', stream, 'Command - ', commandstr)
    await redis.xadd(stream, {'cmd': commandstr})


async def read_from_stream(
    redis: aioredis.Redis, stream: str, latest_id: str = None, past_ms: int = None, last_n: int = None
):
    timeout_ms = 60 * 1000
    while True:
        try:
            if latest_id is not None:
                for msg in await redis.xread([stream], latest_ids=[latest_id], timeout=timeout_ms):
                    latest_id = msg[1].decode("utf-8")
                    payload = {k.decode("utf-8"): v.decode("utf-8")
                               for k, v in msg[2].items()}
                    retcmd = json.dumps(
                        {"message_id": latest_id, "payload": payload})
                    yield retcmd
            else:
                for msg in await redis.xread([stream], timeout=timeout_ms):
                    print(msg)
                    latest_id = msg[1].decode("utf-8")
                    payload = {k.decode("utf-8"): v.decode("utf-8")
                               for k, v in msg[2].items()}
                    retcmd = json.dumps(
                        {"message_id": latest_id, "payload": payload})
                    yield retcmd
        except Exception as e:
            print('Client Disconnected...')
            return


@app.get('/clear-stream/{stream}')
async def clearData(request: Request, stream: str):
    redis = await aioredis.create_redis("redis://127.0.0.1:6379")
    await clear_stream(redis, stream)


@app.get('/stream-logs/{stream}')
async def runStatus(request: Request, stream: str, latest_id: str = None, past_ms: int = None, last_n: int = None, max_frequency: float = None):
    #to_read_id = latest_id
    redis = await aioredis.create_redis("redis://127.0.0.1:6379")
    messages = read_from_stream(redis, stream, latest_id, past_ms, last_n)
    print(messages)
    return EventSourceResponse(messages)


@app.get('/push-logs/{stream}')
async def pushStatus(request: Request, stream: str, commandstr: str):
    #to_read_id = latest_id
    redis = await aioredis.create_redis("redis://127.0.0.1:6379")
    await write_to_stream(redis, stream, commandstr)


#uvicorn.run(app, host="10.12.132.143", port=8082, debug=True)
