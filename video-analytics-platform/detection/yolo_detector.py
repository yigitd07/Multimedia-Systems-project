import paho.mqtt.client as mqtt
import json
from ultralytics import YOLO
import cv2
from collections import Counter
import csv
from datetime import datetime
import threading
import os

class YOLODetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.last_counts = {}
        self.lock = threading.Lock()

        # CSV dosyasını başlat
        self.log_file = "detections.csv"
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "class", "count"])

        # MQTT client'ı oluştur
        self.mqtt_client = mqtt.Client()
        try:
            self.mqtt_client.connect("localhost", 1883, 60)
        except Exception as e:
            print("MQTT bağlantı hatası:", e)

    def detect(self, frame):
        results = self.model(frame)[0]
        annotated_frame = results.plot()

        class_names = [results.names[int(cls)] for cls in results.boxes.cls]
        count = Counter(class_names)
        self.last_counts = dict(count)

        # CSV'ye ve MQTT'ye logla
        self.log_detections(count)

        return annotated_frame

    def get_last_counts(self):
        return self.last_counts

    def log_detections(self, count_dict):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            with open(self.log_file, mode="a", newline="") as f:
                writer = csv.writer(f)
                for class_name, value in count_dict.items():
                    writer.writerow([timestamp, class_name, value])

                    # MQTT ile sadece 'person' tespitini yayınla (örnek)
                    if class_name == "person" and value > 0:
                        msg = {
                            "timestamp": timestamp,
                            "class": class_name,
                            "count": value
                        }
                        self.mqtt_client.publish("alert/person_detected", json.dumps(msg))
