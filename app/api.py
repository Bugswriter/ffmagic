import os
import dataset
from fastapi import FastAPI
from .recorder import Recorder
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import *

app = FastAPI()
app.mount('/static', StaticFiles(directory=f"{os.getcwd()}/static"), name="static")
running_streams = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StreamIn(BaseModel):
	rtsp_url: str
	user_id: int
	camera_id: int

def connect_database():
	return dataset.connect("sqlite:///stream.db")

@app.post("/list_stream")
async def list_stream():
	camera_ids = []
	for key, _ in running_streams.items():
		camera_ids.append(key)
		
	return camera_ids

@app.post("/add_stream")
async def add_stream(_stream: StreamIn):
	""" Adding new rtsp stream into database and start recording """
	db = connect_database()
	table = db["streams"]
	table.insert({
		"rtsp_url": _stream.rtsp_url,
		"user_id": _stream.user_id,
		"camera_id": _stream.camera_id
	})
	stream = Recorder(_stream.rtsp_url, _stream.user_id, _stream.camera_id)
	stream.start()
	running_streams[_stream.camera_id] = stream
	db.close()
	return {'message': 'success'}

@app.post("/remove_stream")
async def remove_stream(_camera_id: int):
	""" Stop stream process and remove from database """
	db = connect_database()
	table = db["streams"]
	table.delete(camera_id=_camera_id)
	stream = running_streams.get(_camera_id)
	if stream:
		stream.stop()
	db.close()
	return {'message': 'success'}
	
@app.on_event("startup")
async def startup_event():
	db = connect_database()
	for stream in db["streams"]:
		key = stream["camera_id"]
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
