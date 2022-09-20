import dataset
from fastapi import FastAPI
from .recorder import Recorder

app = FastAPI()
running_streams = {}

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
