# multi-camera-vehicle-tracking
# camera_server.py
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

from camera_ingest.stream_controller import BaseCamera
import time
import cv2

class Camera(BaseCamera):

    def __init__(self, feed_type, device, port_list):
        super(Camera, self).__init__(feed_type, device, port_list)

    @staticmethod
    def server_frames(image_hub):
        num_frames = 0
        total_time = 0

        while True:  # main loop
            time_start = time.time()

            identity, frame = image_hub.recv_image()

            # Unpack identity tuple if present
            if isinstance(identity, tuple) and len(identity) > 1:
                stream_id = identity[0]
                model_path = identity[1]
            else:
                stream_id = identity
                model_path = "unknown"

            # Split into cam_id and uuid if possible
            if "|" in stream_id:
                cam_id, uuid = stream_id.split("|", 1)
            else:
                cam_id = stream_id
                uuid = "unknown"

            print(f"[SERVER] Received frame from: {cam_id} | UUID: {uuid}")

            image_hub.send_reply(b'OK')  # imagezmq REQ/REP pattern

            num_frames += 1
            total_time += time.time() - time_start
            fps = num_frames / total_time

            # Optionally display FPS on frame
            # cv2.putText(frame, f"FPS: {fps:.2f}", (20, 40), 0, 0.5, (255, 255, 255), 2)

            yield stream_id, frame  # Yield unified stream ID (camera_id|uuid) and frame

