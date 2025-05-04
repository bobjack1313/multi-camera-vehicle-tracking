# multi-camera-vehicle-tracking
# ui_routes.py
# Copyright (C) 2025 Bob Jack
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


import os
import glob
from flask import Response, Blueprint, render_template, request, jsonify, session, redirect
from flask import send_file, stream_with_context
from utils.streaming import stream_registry
import cv2
import imagezmq

# Set up image hub only if this is the main thread
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    image_hub = imagezmq.ImageHub(open_port="tcp://*:5556")
else:
    image_hub = None

ui_bp = Blueprint("ui_routes", __name__)

@ui_bp.route('/')
def index():
    video_dir = "video_data/videos"
    model_dir = "models/yolo"

    existing_videos = glob.glob(os.path.join(video_dir, "*.mp4"))
    available_models = glob.glob(os.path.join(model_dir, "*.pt"))

    selected_model = session.get("selected_model", "models/yolo/roboflow_r5_best.pt")  # fallback

    return render_template(
        "index.html",
        existing_videos=existing_videos,
        available_models=available_models,
        selected_model=selected_model
    )


@ui_bp.route('/video_feed/yolo/<stream_id>')
def video_feed(stream_id):
    print(f"[VIDEO_FEED] Called with stream_id={stream_id}")
    print(f"[VIDEO_FEED] Available registry keys: {list(stream_registry.keys())}")

    stream = stream_registry.get(stream_id)
    if not stream:
        print(f"[VIDEO_FEED] No active stream matches stream_id: {stream_id}")
        return "Stream not found", 404

    port = stream.get("port")
    print(f"[VIDEO_FEED] Redirecting to stream at port {port}")

    #return redirect(f"/internal_proxy/{port}/video")

    return redirect(f"http://localhost:{port}/video")

