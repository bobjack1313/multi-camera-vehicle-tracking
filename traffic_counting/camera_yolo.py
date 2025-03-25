import cv2
import numpy as np
import datetime
from collections import Counter, deque
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self, feed_type, device, port_list):
        super(Camera, self).__init__(feed_type, device, port_list)

    @staticmethod
    def intersect(A, B, C, D):
        return Camera.ccw(A, C, D) != Camera.ccw(B, C, D) and Camera.ccw(A, B, C) != Camera.ccw(A, B, D)

    @staticmethod
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    @staticmethod
    def vector_angle(midpoint, previous_midpoint):
        x = midpoint[0] - previous_midpoint[0]
        y = midpoint[1] - previous_midpoint[1]
        return np.degrees(np.arctan2(y, x))

    @staticmethod
    def yolo_frames(image_hub, unique_name):
        cam_id = unique_name[1]
        print(f"[Camera {cam_id}] Starting YOLOv8 + Deep SORT stream...")

        model = YOLO("yolov8n.pt")  # Swap with yolov8s.pt or custom model if needed
        tracker = DeepSort(max_age=30)

        count_dict = {}
        class_counter = Counter()
        already_counted = deque(maxlen=100)
        intersect_info = []
        memory = {}

        total_counter, up_count, down_count = 0, 0, 0
        current_date = datetime.datetime.now().date()

        while True:
            cam_name, frame = image_hub.recv_image()
            #print(f"[{cam_name}] Frame received by YOLO thread.")
            image_hub.send_reply(b'OK')

            results = model(frame, verbose=False)[0]

            detections = []
            for box, conf, cls in zip(results.boxes.xyxy.cpu().numpy(),
                                       results.boxes.conf.cpu().numpy(),
                                       results.boxes.cls.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)
                detections.append(([x1, y1, x2, y2], conf, int(cls)))

            tracks = tracker.update_tracks(detections, frame=frame)
            #print(f"[DEBUG] cam_name = {cam_name}")

            if cam_name == 'Camera 1':
                line = [(int(0.3 * frame.shape[1]), 0), (int(0.3 * frame.shape[1]), frame.shape[0])]
                #line = [(0, int(0.5 * frame.shape[0])), (frame.shape[1], int(0.5 * frame.shape[0]))]
            else:
                #line = [(0, int(0.3 * frame.shape[0])), (frame.shape[1], int(0.3 * frame.shape[0]))]
                #line = [(int(0.3 * frame.shape[1]), 0), (int(0.3 * frame.shape[1]), frame.shape[0])]
                line = [(0, int(0.7 * frame.shape[0])), (int(frame.shape[1]), int(0.7 * frame.shape[0]))]

            cv2.line(frame, line[0], line[1], (0, 255, 255), 2)

            for track in tracks:
                if not track.is_confirmed():
                    continue
                track_id = track.track_id
                ltrb = track.to_ltrb()
                cls_name = track.get_det_class()

                midpoint = ((ltrb[0] + ltrb[2]) // 2, (ltrb[1] + ltrb[3]) // 2)
                origin_midpoint = (midpoint[0], frame.shape[0] - midpoint[1])

                if track_id not in memory:
                    memory[track_id] = deque(maxlen=2)
                memory[track_id].append(midpoint)

                if len(memory[track_id]) < 2:
                    continue
                previous_midpoint = memory[track_id][0]
                origin_prev = (previous_midpoint[0], frame.shape[0] - previous_midpoint[1])

                if Camera.intersect(midpoint, previous_midpoint, line[0], line[1]) and track_id not in already_counted:
                    total_counter += 1
                    class_counter[cls_name] += 1
                    already_counted.append(track_id)
                    intersection_time = datetime.datetime.now().replace(microsecond=0)
                    angle = Camera.vector_angle(origin_midpoint, origin_prev)
                    intersect_info.append([cls_name, origin_midpoint, angle, intersection_time])
                    if angle > 0: up_count += 1
                    if angle < 0: down_count += 1

                # Draw box and label
                cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), (255, 255, 255), 2)
                cv2.putText(frame, f"ID: {track_id}", (int(ltrb[0]), int(ltrb[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"{cls_name}", (int(ltrb[0]), int(ltrb[3])),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Draw total counter
            direction_label = "up", "down"

            if cam_name == 'Camera 1': 
                direction_label = "left", "right"

            cv2.putText(frame, f"Total: {total_counter} ({up_count} {direction_label[0]}, {down_count} {direction_label[1]})",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Optional: display class counts live
            y = 50
            for cls, count in class_counter.items():
                cv2.putText(frame, f"{cls}: {count}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                y += 20

            yield cam_name, frame
