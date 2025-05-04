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

# multi-camera-vehicle-tracking
# stream_feeder.py
# Copyright (C) 2025 Bob Jack

import cv2
import argparse
import imagezmq
from flask import Flask, Response
import threading
import time

latest_frame = None

# from werkzeug.serving import make_server

# class FlaskThread(threading.Thread):
#     def __init__(self, app, port):
#         threading.Thread.__init__(self)
#         self.port = port
#         self.server = make_server('0.0.0.0', port, app)
#         self.ctx = app.app_context()
#         self.ctx.push()
#         self.daemon = True

#     def run(self):
#         print(f"[Flask] MJPEG feed available at http://localhost:{self.port}/video")
#         self.server.serve_forever()



def create_streamer(source, stream_id="Camera 0", connect_to='tcp://127.0.0.1:5555',
                    loop=True, width=1280, height=720, model_path="models/yolo/yolov8n_dev1.pt"):
    global latest_frame

    print(f"[{stream_id}] Starting stream to {connect_to}")
    print(f"[{stream_id}] Sending model path: {model_path}")

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
            latest_frame = frame.copy()
            sender.send_image((stream_id, model_path), frame)
        else:
            print(f"[{stream_id}] Frame read failed. Reinitializing..." if loop else f"[{stream_id}] End of stream.")
            if loop:
                cap = cv2.VideoCapture(source)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            else:
                break


# @app.route("/video")
# def video():
#     def generate():
#         while True:
#             if latest_frame is not None:
#                 _, buffer = cv2.imencode('.jpg', latest_frame)
#                 yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
#                        buffer.tobytes() + b'\r\n')
#             time.sleep(0.05)
#     return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


from werkzeug.serving import make_server

# class FlaskThread(threading.Thread):
#     def __init__(self, app, port):
#         threading.Thread.__init__(self)
#         self.server = make_server("0.0.0.0", port, app)
#         self.ctx = app.app_context()
#         self.ctx.push()
#         self.daemon = True

#     def run(self):
#         print(f"[Flask] MJPEG feed available at http://localhost:{self.server.port}/video")
#         self.server.serve_forever()


# def run_flask_server(port):
#     flask_app = Flask(__name__)

#     @flask_app.route("/video")
#     def video():
#         def generate():
#             while True:
#                 if latest_frame is not None:
#                     _, buffer = cv2.imencode('.jpg', latest_frame)
#                     yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
#                            buffer.tobytes() + b'\r\n')
#                 time.sleep(0.05)
#         return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

#     thread = FlaskThread(flask_app, port)
#     thread.start()

from werkzeug.serving import make_server

def run_flask_server(port):
    flask_app = Flask(__name__)

    @flask_app.route("/video")
    def video():
        def generate():
            while True:
                if latest_frame is not None:
                    _, buffer = cv2.imencode('.jpg', latest_frame)
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
                           buffer.tobytes() + b'\r\n')
                time.sleep(0.05)
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    print(f"[Flask] MJPEG feed available at http://localhost:{port}/video")

    # ✅ Safe threaded server
    server = make_server("0.0.0.0", port, flask_app)
    server.serve_forever()



# def run_flask_server(port):
#     flask_app = Flask(__name__)

#     @flask_app.route("/video")
#     def video():
#         def generate():
#             while True:
#                 if latest_frame is not None:
#                     _, buffer = cv2.imencode('.jpg', latest_frame)
#                     yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
#                            buffer.tobytes() + b'\r\n')
#                 time.sleep(0.05)
#         return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

#     print(f"[Flask] MJPEG feed available at http://localhost:{port}/video")

#     # START SAFE SERVER INSIDE THREAD
#     server = make_server('0.0.0.0', port, flask_app)
#     server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Universal stream feeder (video file or RTSP).")
    parser.add_argument("--model-path", type=str, default="models/yolo/yolov8n_dev1.pt")
    parser.add_argument('--source', required=True, help="Path to video file or RTSP stream URL.")
    parser.add_argument('--camera-id', required=True, help="Stream ID (camera_id|uuid).")
    parser.add_argument('--connect-to', default='tcp://127.0.0.1:5555', help="ZMQ connection address.")
    parser.add_argument('--loop', action='store_true', help="Loop video when end is reached.")
    parser.add_argument('--flask-port', type=int, default=None)
    parser.add_argument('--width', type=int, default=1280, help="Frame width.")
    parser.add_argument('--height', type=int, default=720, help="Frame height.")
    args = parser.parse_args()

    stream_id = args.camera_id

    if args.flask_port:
        threading.Thread(target=run_flask_server, args=(args.flask_port,), daemon=True).start()
    else:
        raise ValueError("Missing --flask-port")

    # Start video stream
    create_streamer(
        source=args.source,
        stream_id=stream_id,
        connect_to=args.connect_to,
        loop=args.loop,
        width=args.width,
        height=args.height,
        model_path=args.model_path
    )
