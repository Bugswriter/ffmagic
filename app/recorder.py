import os
import asyncio
import typing
from ffmpeg import FFmpeg
from asyncio.subprocess import Process

def get_recorder(rtsp_url: str, user_id: int, camera_id: int):
	segment_duration = 30	
	record_path = f"/tmp/ffmagic/rec/user_{user_id}/camera_{camera_id}/%s.mp4"
	hls_path = f"/tmp/ffmagic/hls/user_{user_id}/camera_{camera_id}/index.m3u8"

	os.makedirs(record_path[:-7], exist_ok=True)
	os.makedirs(hls_path[:-11], exist_ok=True)
	
	ffmpeg = FFmpeg().option('y').input(
		rtsp_url,
		rtsp_transport='tcp',
		rtsp_flags="prefer_tcp"
	).output(
		record_path,
		{"codec:v": "copy"},
		an=None,
		f="segment",
		segment_time=segment_duration,
		segment_atclocktime=1,
		reset_timestamps=1,
		strftime=1
	).output(
		hls_path,
		hls_list_size=4,
		tune="zerolatency",
		hls_allow_cache=0
	)
	
	@ffmpeg.on('stderr')
	def on_stderr(error):
		pass

	@ffmpeg.on('progress')
	def on_progress(progress):
		print(f"[Camera({camera_id}), User({user_id})]: {progress}")

	@ffmpeg.on('terminated')
	def on_terminated():
		print(f"[Camera({camera_id}), User({user_id})]: Terminated")

	@ffmpeg.on('error')
	def on_error(code):
		print(f"[Camera({camera_id}), User({user_id})]: Error -> {code}")

	return ffmpeg


class Recorder:
	def __init__(self, rtsp_url: str, user_id: int, camera_id: int):
		self.ffmpeg = get_recorder(rtsp_url, user_id, camera_id)

	def is_running(self):
		process = typing.cast(Process, self.ffmpeg._process)
		if process is None or process.returncode is not None:
			return False
		return True

	def start(self):
		if self.is_running():
			return
		
		asyncio.create_task(self.ffmpeg.execute())

	def stop(self):
		if self.is_running():
			self.ffmpeg.terminate()

