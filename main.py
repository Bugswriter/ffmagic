import os
import uvicorn 
from app import app
from app.config import *

if __name__=="__main__":
	os.makedirs(f"{STORAGE_DIR}", exist_ok=True)
	uvicorn.run(app, host="0.0.0.0", port=8002)
