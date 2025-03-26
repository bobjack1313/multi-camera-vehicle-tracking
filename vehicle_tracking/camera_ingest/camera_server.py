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

            cam_id, frame = image_hub.recv_image()
            image_hub.send_reply(b'OK')  # this is needed for the stream to work with REQ/REP pattern

            num_frames += 1

            time_now = time.time()
            total_time += time_now - time_start
            fps = num_frames / total_time

            # uncomment below to see FPS of camera stream
            # cv2.putText(frame, "FPS: %.2f" % fps, (int(20), int(40 * 5e-3 * frame.shape[0])), 0, 2e-3 * frame.shape[0],(255, 255, 255), 2)

            yield cam_id, frame
