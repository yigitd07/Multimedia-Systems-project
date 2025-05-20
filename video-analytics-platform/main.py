import cv2
from detection.yolo_detector import YOLODetector

def main():
    detector = YOLODetector()

    cap = cv2.VideoCapture(0)  # Laptop kamerası

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        annotated = detector.detect(frame)
        cv2.imshow("YOLOv8 Detection", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
