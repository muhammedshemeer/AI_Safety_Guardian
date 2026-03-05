import cv2
import numpy as np
from ultralytics import YOLO

def detect_fall(frame, model):
    """
    Detects if a person has fallen based on pose estimation.
    Returns: {"fall_detected": bool, "confidence": float}
    """
    results = model(frame, verbose=False)
    fall_detected = False
    confidence = 0.0

    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Get coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            w = x2 - x1
            h = y2 - y1
            conf = float(box.conf[0])

            # Check aspect ratio (width > height indicates horizontal posture)
            aspect_ratio = w / h
            
            # Simple logic: if someone is significantly wider than they are tall, 
            # they are likely lying down.
            if aspect_ratio > 1.2 and conf > 0.5:
                fall_detected = True
                confidence = conf
                
                # Draw bounding box and label
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                cv2.putText(frame, f"Fall Risk Detected! ({conf:.2f})", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                # Normal posture
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"Person ({conf:.2f})", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return {
        "fall_detected": fall_detected,
        "confidence": confidence
    }

if __name__ == "__main__":
    # Test script for local run
    print("Loading YOLOv8 Pose model...")
    model = YOLO('yolov8n-pose.pt')
    
    cap = cv2.VideoCapture(0)
    print("Starting webcam... Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame, is_fall, conf = detect_fall(frame, model)
        
        cv2.imshow("Fall Detection Test", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
