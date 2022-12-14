# A simple DVR system I made for fun.


## Installation
```sh
python -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python3 main.py
```

Visit - [[http://127.0.0.1:8000][http://127.0.0.1:8000]]
for UI.

# About this project.
In my previous company I was working with RTSP streams.
While working on it, I got interested and decided to write
this project.
My objective was simple. Make a API for storing RTSP streams
in backend servers. Also manage it.
I used async multiprocessing to spawn a new process for
each RTSP stream. It's very simple but useful.
