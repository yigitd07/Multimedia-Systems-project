from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
import cv2
from detection.yolo_detector import YOLODetector
import threading
import time

app = FastAPI()
detector = YOLODetector()

# Global değişkenler
cap = None
running = False
lock = threading.Lock()
analyzer_thread = None

def generate_frames():
    global cap, running
    while True:
        with lock:
            if not running or cap is None:
                time.sleep(0.1)
                continue
            success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        annotated = detector.detect(frame)
        _, buffer = cv2.imencode('.jpg', annotated)
        frame_bytes = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

def analyze_loop():
    global cap, running
    while True:
        with lock:
            if not running or cap is None:
                time.sleep(0.1)
                continue
            success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue
        detector.detect(frame)
        time.sleep(0.1)

@app.post("/start")
def start_stream():
    global cap, running, analyzer_thread
    with lock:
        if running:
            return {"message": "Stream already running"}

        # GStreamer pipeline kullanmak için bunu True yap
        use_gstreamer = False  # ← değiştirmek istersen burayı True yap

        if use_gstreamer:
            # GStreamer pipeline örneği (Linux için /dev/video0)
            gst_pipeline = (
                "v4l2src device=/dev/video0 ! "
                "video/x-raw, width=640, height=480, framerate=30/1 ! "
                "videoconvert ! appsink"
            )
            cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
        else:
            # Standart OpenCV kamera
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return {"message": "Failed to open camera"}

        running = True

    analyzer_thread = threading.Thread(target=analyze_loop, daemon=True)
    analyzer_thread.start()

    return {"message": "Stream started"}

@app.post("/stop")
def stop_stream():
    global cap, running
    with lock:
        if not running:
            return {"message": "Stream already stopped"}
        running = False
        if cap is not None:
            cap.release()
            cap = None
    return {"message": "Stream stopped"}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/status")
def get_status():
    return {
        "streaming": running,
        "detections": detector.get_last_counts()
    }

@app.get("/status-page")
def status_page():
    return FileResponse("static/status.html")
