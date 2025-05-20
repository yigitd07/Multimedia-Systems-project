from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Basit veri yapısı: örnek ayarlar
stream_status = {"camera_0": False}
settings = {"resolution": "640x480", "fps": 30, "bitrate": "1Mbps"}

class StreamCommand(BaseModel):
    camera_id: str

class StreamSettings(BaseModel):
    resolution: str
    fps: int
    bitrate: str

@app.get("/")
def home():
    return {"message": "Video Analytics API"}

@app.post("/start")
def start_stream(data: StreamCommand):
    stream_status[data.camera_id] = True
    return {"status": f"Started stream for {data.camera_id}"}

@app.post("/stop")
def stop_stream(data: StreamCommand):
    stream_status[data.camera_id] = False
    return {"status": f"Stopped stream for {data.camera_id}"}

@app.post("/settings")
def update_settings(new_settings: StreamSettings):
    settings.update(new_settings.dict())
    return {"message": "Settings updated", "new_settings": settings}

@app.get("/status")
def get_status():
    return {
        "stream_status": stream_status,
        "settings": settings
    }
