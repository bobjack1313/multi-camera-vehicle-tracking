# multi-camera-vehicle-tracking
# stream_contoller.py
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
import threading
import imagezmq

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent:
    def __init__(self):
        self.events = {}

    def wait(self):
        ident = get_ident()
        if ident not in self.events:
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                event[0].set()
                event[1] = now
            elif now - event[1] > 5:
                remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        self.events[get_ident()][0].clear()


class BaseCamera:
    threads = {}        # Map of stream_id → thread
    frame = {}          # Map of stream_id → frame
    last_access = {}    # Map of stream_id → last viewer timestamp
    event = {}          # Map of stream_id → CameraEvent()

    def __init__(self, feed_type, device, port, model_path=None):
        self.stream_id = f"{device}" if "|" in device else f"{feed_type}|{device}"  # device is stream_id now
        self.model_path = model_path

        if self.stream_id not in BaseCamera.event:
            BaseCamera.event[self.stream_id] = CameraEvent()

        if self.stream_id not in BaseCamera.threads or BaseCamera.threads[self.stream_id] is None:
            BaseCamera.last_access[self.stream_id] = time.time()
            BaseCamera.threads[self.stream_id] = threading.Thread(
                target=self._thread,
                args=(self.stream_id, port, model_path),
                daemon=True
            )
            BaseCamera.threads[self.stream_id].start()

            while self.get_frame(self.stream_id) is None:
                time.sleep(0)

    @classmethod
    def get_frame(cls, stream_id):
        BaseCamera.last_access[stream_id] = time.time()
        BaseCamera.event[stream_id].wait()
        BaseCamera.event[stream_id].clear()
        return BaseCamera.frame.get(stream_id)

    @classmethod
    def remove_stream(cls, stream_id):
        cls.frame.pop(stream_id, None)
        cls.event.pop(stream_id, None)
        cls.last_access.pop(stream_id, None)
        cls.threads.pop(stream_id, None)


    @staticmethod
    def frames():
        raise RuntimeError("Subclasses must implement this.")

    @staticmethod
    def yolo_frames(image_hub, stream_id, model_path=None):
        raise NotImplementedError("Subclasses must implement this.")

    @staticmethod
    def server_frames(image_hub):
        raise RuntimeError("Subclasses must implement this.")

    @classmethod
    def yolo_thread(cls, stream_id, port, model_path=None):
        image_hub = imagezmq.ImageHub(open_port=f"tcp://*:{port}")
        for frame in cls.yolo_frames(image_hub, stream_id, model_path=model_path):
            cls.frame[stream_id] = frame
            cls.event[stream_id].set()
            if time.time() - cls.last_access[stream_id] > 60:
                print(f"[YOLO] Stream {stream_id} inactive. Closing.")
                break

    @classmethod
    def server_thread(cls, stream_id, port):
        image_hub = imagezmq.ImageHub(open_port=f"tcp://*:{port}")
        for recv_id, frame in cls.server_frames(image_hub):
            cls.frame[recv_id] = frame
            cls.event[recv_id] = cls.event.get(recv_id, CameraEvent())
            cls.event[recv_id].set()
            cls.last_access[recv_id] = time.time()
            if time.time() - cls.last_access[recv_id] > 5:
                print(f"[SERVER] Stream {recv_id} inactive. Closing port {port}")
                break

    @classmethod
    def _thread(cls, stream_id, port, model_path=None):
        feed_type = stream_id.split("|")[0]
        if feed_type == "camera":
            cls.server_thread(stream_id, port)
        elif feed_type == "yolo":
            cls.yolo_thread(stream_id, port, model_path)
        BaseCamera.threads[stream_id] = None

