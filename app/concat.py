import os
import subprocess
import glob
from .config import *

def make_concat_file(base_path: str, start: int, end: int):
	videos_path =  base_path + "/*.mp4"
	concat_file_path = base_path + "/concat.txt"
	
	if os.path.exists(concat_file_path):
		os.remove(concat_file_path)
		
	f = open(concat_file_path, 'a')
	for video in glob.glob(videos_path):
		if os.path.split(video)[-1] == "stream.mp4":
			continue
		
		video_timestamp = int(os.path.split(video)[-1][:-4])
		if start <= video_timestamp and end >= video_timestamp:
			f.write(f"file '{video}'\n")

	f.close()

def make_concat_stream(base_path):
	concat_file_path = base_path + "/concat.txt"
	stream_file_path = base_path + "/stream.mp4"
	cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", '0', "-i", concat_file_path, "-c", "copy", stream_file_path]
	return subprocess.run(cmd).returncode
	

def make_concat(user_id: int, camera_id: int, start: int, end: int):
	base_path = f"{STORAGE_DIR}/rec/user_{user_id}/camera_{camera_id}"
	make_concat_file(base_path, start, end)
	if make_concat_stream(base_path) == 0:
		return f"/dvr/rec/user_{user_id}/camera_{camera_id}/stream.mp4"
	else:
		return None
