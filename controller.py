from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO('yolo11n-pose.pt')  # Using YOLO v11 model

def track_objects_in_frame(frame):
    results = model(frame, stream=True)  # Use stream=True for better performance
    tracked_objects = []

    for r in results:
        boxes = r.boxes
        keypoints = r.keypoints
        if boxes is not None and keypoints is not None:
            for box, kpts in zip(boxes, keypoints):
                confidence = box.conf.item()  # Get confidence score
                class_id = box.cls.item()  # Get class ID

                # Ensure keypoints are in the correct format
                keypoints_array = kpts.xy.cpu().numpy()
                if len(keypoints_array.shape) == 3:
                    keypoints_array = keypoints_array.squeeze(0)

                # Normalize keypoints
                frame_height, frame_width = frame.shape[:2]
                normalized_keypoints = {}
                for i, kp in enumerate(keypoints_array):
                    x, y = kp[:2]  # Only use the first two values (x, y) of each keypoint
                    normalized_keypoints[f'kp_{i}'] = (x / frame_width, y / frame_height)

                tracked_objects.append({
                    'confidence': confidence,
                    'class_id': class_id,
                    'keypoints': normalized_keypoints
                })
    return tracked_objects

def main():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        tracked_objects = track_objects_in_frame(frame)
        for obj in tracked_objects:
            confidence = obj['confidence']
            class_id = obj['class_id']
            keypoints = obj['keypoints']
    
            # Draw keypoints
            for kp_name, (x, y) in keypoints.items():
                cv2.circle(frame, (int(x * frame.shape[1]), int(y * frame.shape[0])), 3, (0, 0, 255), -1)
            
            # Display confidence and class ID
            label = f"Class: {int(class_id)}, Conf: {confidence:.2f}"
            cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
