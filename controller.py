from ultralytics import YOLO
import cv2
import numpy as np
import threading
import queue

model = YOLO('yolo11n-pose.pt')
hand_heights_queue = queue.Queue()

def track_objects_in_frame(frame):
    results = model(frame)

    tracked_objects = []
    for result in results:
        normalized_keypoints = extract_keypoints(result, frame.shape[1], frame.shape[0])
        if normalized_keypoints:
            tracked_objects.extend(normalized_keypoints)
    
    print("Tracked Objects Structure:", tracked_objects)
    
    return tracked_objects

def get_hand_heights(tracked_objects):
    hand_heights = []
    for obj in tracked_objects:
        left_hand, right_hand = obj.get('hand_positions', (None, None))
        frame_height = obj.get('frame_height', 1)
        if left_hand:
            height = 1 - (left_hand[1] / frame_height)
            hand_heights.append(height)
        if right_hand:
            height = 1 - (right_hand[1] / frame_height)
            hand_heights.append(height)
    
    return hand_heights

def run_tracking():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        frame_height, frame_width = frame.shape[:2]
        tracked_objects = track_objects_in_frame(frame)
        
        for obj in tracked_objects:
            keypoints = obj['keypoints']
            left_hand, right_hand = compute_overall_hand_positions(keypoints, frame_width, frame_height)
            obj['hand_positions'] = (left_hand, right_hand)
            obj['frame_height'] = frame_height
        
        hand_heights = get_hand_heights(tracked_objects)
        
        hand_heights_queue.put(hand_heights)
        
        for obj in tracked_objects:
            left_hand, right_hand = obj.get('hand_positions', (None, None))

            if left_hand:
                cv2.circle(frame, left_hand, 10, (255, 0, 0), -1)
            if right_hand:
                cv2.circle(frame, right_hand, 10, (0, 0, 255), -1)

        bar_height = 100
        bar_width = 30
        gap = 10
        start_x = 10
        start_y = frame.shape[0] - 110

        for i, height in enumerate(hand_heights):
            bar_top = int(start_y + bar_height * (1 - height))

            cv2.rectangle(frame, (start_x, start_y), (start_x + bar_width, bar_top), (0, 255, 0), -1)
            cv2.rectangle(frame, (start_x, start_y), (start_x + bar_width, start_y + bar_height), (255, 255, 0), 2)

            label = f"Ch {i+1}"
            cv2.putText(frame, label, (start_x, start_y + bar_height + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            value = f"{height:.2f}"
            cv2.putText(frame, value, (start_x, bar_top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            start_x += bar_width + gap

        cv2.imshow('Hand Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def extract_keypoints(result, frame_width, frame_height):
    keypoints = result.keypoints
    if keypoints is not None:
        keypoints_array = keypoints.xy.cpu().numpy()
        normalized_keypoints = []
        for person_kps in keypoints_array:
            person = {'keypoints': {}}
            for i in range(person_kps.shape[0]):
                x, y = person_kps[i]
                person['keypoints'][f'kp_{i}'] = (x / frame_width, y / frame_height)
            normalized_keypoints.append(person)
        return normalized_keypoints
    return []

def compute_overall_hand_positions(keypoints, frame_width, frame_height):
    if not keypoints:
        return None, None

    points = np.array(list(keypoints.values()))
    points = points[np.any(points != 0, axis=1)]

    if points.size == 0:
        return None, None

    leftmost_idx = np.argmin(points[:, 0])
    rightmost_idx = np.argmax(points[:, 0])

    left_hand = points[leftmost_idx]
    right_hand = points[rightmost_idx]

    left_hand_px = (int(left_hand[0] * frame_width), int(left_hand[1] * frame_height))
    right_hand_px = (int(right_hand[0] * frame_width), int(right_hand[1] * frame_height))

    return left_hand_px, right_hand_px

def start_tracking_thread():
    tracking_thread = threading.Thread(target=run_tracking)
    tracking_thread.daemon = True
    tracking_thread.start()
    return tracking_thread

def get_current_hand_heights():
    try:
        return hand_heights_queue.get_nowait()
    except queue.Empty:
        return None

if __name__ == "__main__":
    tracking_thread = start_tracking_thread()
    tracking_thread.join()
