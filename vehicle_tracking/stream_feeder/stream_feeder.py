# multi-camera-vehicle-tracking
# stream_feeder.py
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


import cv2
import argparse
import os
import imagezmq

# This is a combination of camera_client and video_streamer to make streaming dynamic
def create_streamer(source, cam_id="Camera 0", connect_to='tcp://127.0.0.1:5555',
    loop=True, width=1280, height=720, model_path="models/yolo/yolov8n_dev1.pt"):

    print(f"[{cam_id}] Starting stream to {connect_to}")
    print(f"[{cam_id}] Sending model path: {model_path}")

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video source: {source}")

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    sender = imagezmq.ImageSender(connect_to=connect_to)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            print(f"[{cam_id}] Sending frame #{frame_count}")
            # sender.send_image(cam_id, frame)
            sender.send_image((cam_id, model_path), frame)

        else:
            print(f"[{cam_id}] Frame read failed. Reinitializing..." if loop else f"[{cam_id}] End of stream.")
            if loop:
                cap = cv2.VideoCapture(source)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            else:
                break

    # while True:
    #     ret, frame = cap.read()

    #     if ret:
    #         sender.send_image(cam_id, frame)

    #     else:
    #         if loop:
    #             cap = cv2.VideoCapture(source)
    #             cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #             cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #         else:
    #             print(f"[{cam_id}] Stream ended.")
    #             break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Universal stream feeder (video file or RTSP).")
    parser.add_argument("--model-path", type=str, default="models/yolo/yolov8n_dev1.pt")
    parser.add_argument('--source', required=True, help="Path to video file or RTSP stream URL.")
    parser.add_argument('--camera-id', required=True, help="Unique camera ID label (e.g., 'Camera 0').")
    parser.add_argument('--connect-to', default='tcp://127.0.0.1:5555', help="ZMQ connection address.")
    parser.add_argument('--loop', action='store_true', help="Loop video when end is reached.")
    parser.add_argument('--width', type=int, default=1280, help="Frame width.")
    parser.add_argument('--height', type=int, default=720, help="Frame height.")
    args = parser.parse_args()

    create_streamer(
        source=args.source,
        cam_id=args.camera_id,
        connect_to=args.connect_to,
        loop=args.loop,
        width=args.width,
        height=args.height,
        model_path=args.model_path
    )
