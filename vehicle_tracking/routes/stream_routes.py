# multi-camera-vehicle-tracking
# stream_routes.py
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

from flask import Blueprint, Response
from importlib import import_module
from utils.streaming import gen


stream_bp = Blueprint('stream_routes', __name__)

MAX_STREAMS = 20
BASE_PORT = 5555

stream_handlers = {
    'camera': 'camera_ingest.camera_server',
    'yolo': 'camera_ingest.camera_yolo'
}

@stream_bp.route('/video_feed/<feed_type>/<device>')
def video_feed(feed_type, device):
    try:
        device = int(device)
    except ValueError:
        return "Invalid device index", 400

    if feed_type not in stream_handlers:
        return f"Unsupported feed type: {feed_type}", 400

    if device < 0 or device >= MAX_STREAMS:
        return f"Camera index out of range (0 to {MAX_STREAMS - 1})", 400

    port = BASE_PORT + device
    camera_stream = import_module(stream_handlers[feed_type]).Camera

    return Response(gen(
        camera_stream=camera_stream(feed_type, device, port),
        feed_type=feed_type,
        device=device
    ), mimetype='multipart/x-mixed-replace; boundary=frame')
