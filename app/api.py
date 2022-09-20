import os
import dataset
import asyncio
from fastapi import FastAPI
from concurrent.futures import ProcessPoolExecutor
import glob
from .recorder import Recorder
from .concat import make_concat
from fastapi.middleware.cors import CORSMiddleware
from .config import *

app = FastAPI()
running_streams = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def connect_database():
	return dataset.connect("sqlite:///stream.db")
	
@app.post("/add_stream")
async def add_stream(rtsp_url: str, user_id: int, camera_id: int):
	db = connect_database()
	table = db["streams"]
	table.insert({
		"rtsp_url": rtsp_url,
		"user_id": user_id,
		"camera_id": camera_id
	})
	stream = Recorder(rtsp_url, user_id, camera_id)
	stream.start()
	db.close()
	return {'message': 'success'}

@app.post("/get_stream")
async def get_stream(user_id: int, camera_id: int, start_timestamp: int, end_timestamp: int):
	loop = asyncio.get_running_loop()
	result = await loop.run_in_executor(
		None,
		make_concat,
		user_id,
		camera_id,
		start_timestamp,
		end_timestamp		
	)
	if result:
		return {'message': result}
	else:
		return {'message': "error making concat"}
	
	
@app.post("/get_all_stream")

async def get_all_stream(user_id: int, start_timestamp: int, end_timestamp: int):
	loop = asyncio.get_running_loop()		
	pool = ProcessPoolExecutor()
	base_path = f"{STORAGE_DIR}/rec/user_{user_id}/camera_*"
	urls = {}
	for camera in glob.glob(base_path):
		camera_id = int(os.path.split(camera)[-1].split('_')[1])
		print(camera_id)
		url = await loop.run_in_executor(
			pool, make_concat, user_id, camera_id, start_timestamp, end_timestamp
		)
		if tmp:
			urls[camera_id] = url
			
	return {'message': urls}


@app.on_event("startup")
async def startup_event():
	db = connect_database()
	for stream in db["streams"]:
		key = stream["user_id"] + stream["camera_id"]
		running_streams[key] = Recorder(
			stream["rtsp_url"],
			stream["user_id"],
			stream["camera_id"],
		)
		running_streams[key].start()
	db.close()

@app.on_event("shutdown")
async def shutdown_event():
	for _, stream in running_streams.items():
		stream.stop()
