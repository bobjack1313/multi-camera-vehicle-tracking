# multi-camera-vehicle-tracking
# streaming.py
# Copyright (C) 2025 Bob Jack
# Originally forked from Multi-Camera Live Object Tracking by Leon Lok (2020)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import time
import cv2


def gen(camera_stream, feed_type, device):
    '''
    Generator function for streaming video frames to the Flask Response object.

    Args:
        camera_stream: An instance of the camera stream class (e.g., Camera from camera_yolo.py).
        feed_type (str): Type of feed, e.g., 'yolo' or 'camera'.
        device (int): The device index.

    Yields:
        byte stream of the JPEG-encoded frame.
    '''
    unique_name = (feed_type, device)
    num_frames = 0
    total_time = 0

    while True:
        start_time = time.time()

        cam_id, frame = camera_stream.get_frame(unique_name)
        if frame is None:
            break

        # Optional overlay: camera ID
        cv2.putText(frame, cam_id, (int(0.75 * frame.shape[1]), int(0.85 * frame.shape[0])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        if feed_type == 'yolo':
            num_frames += 1
            total_time += time.time() - start_time
            fps = num_frames / total_time if total_time > 0 else 0

            # Optional overlay: FPS
            cv2.putText(frame, f"FPS: {fps:.2f}",
                        (int(0.75 * frame.shape[1]), int(0.9 * frame.shape[0])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Encode frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Yield as multipart stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
