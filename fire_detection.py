import cv2
import numpy as np
from ultralytics import YOLO

def detect_fire(frame, model):
    """
    Detects fire or smoke. 
    Returns: {"fire_detected": bool, "confidence": float}
    """
    results = model(frame, verbose=False)
    fire_detected = False
    confidence = 0.0

    # AI Detection Logic
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls]
            if label in ['fire', 'smoke']:
                fire_detected = True
                confidence = max(confidence, conf)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 165, 255), 2)
                cv2.putText(frame, f"{label.capitalize()} ({conf:.2f})", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

    # Simple Color-based fallback
    if not fire_detected:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_fire = np.array([18, 50, 50], dtype="uint8")
        upper_fire = np.array([35, 255, 255], dtype="uint8")
        mask = cv2.inRange(hsv, lower_fire, upper_fire)
        
        if cv2.countNonZero(mask) > 5000:
            fire_detected = True
            confidence = 0.85
            cv2.putText(frame, "Potential Fire Mask Detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return {
        "fire_detected": fire_detected,
        "confidence": confidence
    }

if __name__ == "__main__":
    # Test script
    print("Loading YOLOv8 model...")
    # Note: Use a model trained on fire/smoke for better results
    model = YOLO('yolov8n.pt') 
    
    cap = cv2.VideoCapture(0)
    print("Starting webcam... Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame, is_alert, conf = detect_fire_smoke(frame, model)
        
        cv2.imshow("Fire Detection Test", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
