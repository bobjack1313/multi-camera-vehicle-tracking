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

from flask import Blueprint, request, redirect, url_for, render_template
import subprocess
import os
import uuid
import glob


stream_control_bp = Blueprint('stream_control_routes', __name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'video_data/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@stream_control_bp.route('/add_stream', methods=['GET', 'POST'])
def add_stream():
    if request.method == 'GET':
        print("DEBUG: Globb")
        existing_videos = glob.glob("video_data/videos/*.mp4")
        print("[DEBUG] Found videos:", existing_videos)

        return render_template('add_stream.html', existing_videos=existing_videos)

    else:
        feed_type = request.form.get('feed_type')
        camera_id = request.form.get('camera_id') or f"Camera-{uuid.uuid4().hex[:4]}"
        port = 5555  # TODO: make dynamic

        source = None

        if feed_type == 'video':
            if 'video_file' in request.files and request.files['video_file'].filename:
                video_file = request.files['video_file']
                filename = f"video_data/uploads/{uuid.uuid4().hex}.mp4"
                video_file.save(filename)
                source = filename
            elif request.form.get('existing_file'):
                print("DEBUG: ELIF")
                source = request.form.get('existing_file')
            else:
                return "No video file uploaded or selected", 400

        elif feed_type == 'rtsp':
            source = request.form.get('rtsp_url')
            if not source:
                return "RTSP URL is required", 400

        else:
            return "Invalid feed type", 400

        cmd = [
            "python3", "vehicle_tracking/stream_feeder/stream_feeder.py",
            "--source", source,
            "--camera-id", camera_id,
            "--connect-to", f"tcp://127.0.0.1:{port}",
            "--loop"
        ]

        subprocess.Popen(cmd)
        return redirect(url_for('ui_routes.index'))
