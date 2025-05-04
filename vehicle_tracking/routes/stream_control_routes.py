# multi-camera-vehicle-tracking
# stream_contoll_routes.py
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

from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from utils.streaming import stream_registry
import subprocess
import os
import uuid
import glob
import psutil
import socket

stream_control_bp = Blueprint('stream_control_routes', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'video_data/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_free_port(start=5555, end=5999):
    ''' Finds an available TCP port on localhost. '''

    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free ports available")


@stream_control_bp.route('/api/streams', methods=['GET'])
def get_active_streams():
    session_streams = session.get("active_streams", [])
    cleaned_streams = []

    for stream in session_streams:
        cam_id = stream["camera_id"]
        reg = stream_registry.get(cam_id)
        if reg:
            cleaned_streams.append(stream)

    session["active_streams"] = cleaned_streams
    session.modified = True

    result = []
    for stream in cleaned_streams:
        cam_id = stream["camera_id"]
        reg = stream_registry[cam_id]
        result.append({
            "id": stream["id"],
            "camera_id": cam_id,
            "port": stream.get("port", reg.get("port")),
            "model": reg.get("model", "Unknown"),
            "source": reg.get("source", "Unknown"),
            "feed_type": stream.get("feed_type", "video")
        })

    return jsonify(result)



@stream_control_bp.route('/add_stream', methods=['GET', 'POST'])
def add_stream():
    if request.method == 'GET':
        existing_videos = glob.glob("video_data/videos/*.mp4")
        print("[DEBUG] Found videos:", existing_videos)

        return render_template('add_stream.html', existing_videos=existing_videos)

    # POST logic
    feed_type = request.form.get('feed_type')

    base_name = "Camera"
    i = 0
    camera_id = f"{base_name} {i}"
    while camera_id in stream_registry:
        i += 1
        camera_id = f"{base_name} {i}"

    port = get_free_port()
    model_path = request.form.get("model_path")
    session['selected_model'] = model_path
    source = None

    print(f"[DEBUG] Selected model path: {model_path}")
    print(f"[DEBUG] Feed type: {feed_type}")

    if feed_type == 'video':
        if 'video_file' in request.files and request.files['video_file'].filename:
            video_file = request.files['video_file']
            filename = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}.mp4")
            video_file.save(filename)
            source = filename
        elif request.form.get('existing_file'):
            source = request.form.get('existing_file')
        else:
            return "No video file uploaded or selected", 400

    elif feed_type == 'rtsp':
        source = request.form.get('rtsp_url')
        if not source:
            return "RTSP URL is required", 400
    else:
        return "Invalid feed type", 400

    port = get_free_port()
    cmd = [
        "python3",
        os.path.join(BASE_DIR, "vehicle_tracking", "stream_feeder", "stream_feeder.py"),
        "--source", source,
        "--camera-id", camera_id,
        "--connect-to", f"tcp://127.0.0.1:{port}",
        "--model-path", model_path,
        "--loop"
    ]

    print(f"[DEBUG] Launching stream: {cmd}")
    proc = subprocess.Popen(cmd)

    active_streams = session.get("active_streams", [])
    active_streams.append({
        "id": len(active_streams),
        "camera_id": camera_id,
        "feed_type": feed_type,
        "port": port
    })
    session["active_streams"] = active_streams
    session.modified = True

    stream_registry[camera_id] = {
        "pid": proc.pid,
        "port": port,
        "model": model_path,
        "source": source,
    }

    return redirect(url_for('ui_routes.index'))




@stream_control_bp.route('/stop_stream/<camera_id>', methods=['POST'])
def stop_stream(camera_id):
    print(f"[CONTROL] Attempting to stop stream: {camera_id}")

    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and camera_id in ' '.join(cmdline) and 'stream_feeder.py' in cmdline:
                print(f"[KILL] Found process for {camera_id}: PID={proc.pid}")
                proc.kill()

                # Remove from registry
                stream_registry.pop(camera_id, None)

                return f"Stream for {camera_id} stopped.", 200
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return f"No active stream found for {camera_id}.", 404
