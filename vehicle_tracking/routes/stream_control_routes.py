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
from urllib.parse import unquote
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
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports available")

# def get_free_port(start=5555, end=5999):
#     ''' Finds an available TCP port on localhost. '''

#     for port in range(start, end):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             if s.connect_ex(("127.0.0.1", port)) != 0:
#                 return port
#     raise RuntimeError("No free ports available")



# @stream_control_bp.route('/api/streams', methods=['GET'])
# def get_active_streams():
#     session_streams = session.get("active_streams", [])
#     cleaned_streams = []

#     for stream in session_streams:
#         cam_id = stream["camera_id"]
#         reg = stream_registry.get(cam_id)
#         if reg:
#             cleaned_streams.append(stream)

#     session["active_streams"] = cleaned_streams
#     session.modified = True

#     result = []

#     # for i, stream in enumerate(cleaned_streams):
#     # cam_id = stream["camera_id"]
#     # reg = stream_registry[cam_id]
#     # result.append({
#     #     "id": stream_uuid,
#     #     "camera_id": cam_id,
#     #     "port": stream.get("port", reg.get("port")),
#     #     "model": reg.get("model", "Unknown"),
#     #     "source": reg.get("source", "Unknown"),
#     #     "feed_type": stream.get("feed_type", "video")
#     # })
#     print(f"[API] Returning stream list: {[s['id'] for s in cleaned_streams]}")
#     for stream in cleaned_streams:
#         stream_uuid = stream.get("id") or uuid.uuid4().hex
#         cam_id = stream["camera_id"]
#         reg = stream_registry[cam_id]
#         result.append({
#             "id": stream_uuid,
#             "camera_id": cam_id,
#             "port": stream.get("port", reg.get("port")),
#             "model": reg.get("model", "Unknown"),
#             "source": reg.get("source", "Unknown"),
#             "feed_type": stream.get("feed_type", "video")
#         })

#     return jsonify(result)


@stream_control_bp.route('/api/streams', methods=['GET'])
def get_active_streams():
    session_streams = session.get("active_streams", [])
    cleaned_streams = []

    for stream in session_streams:
        cam_id = stream.get("camera_id")
        stream_id = stream.get("id")
        full_key = f"{cam_id}|{stream_id}"

        reg = stream_registry.get(full_key)
        if reg:
            cleaned_streams.append(stream)

    session["active_streams"] = cleaned_streams
    session.modified = True

    result = []
    for stream in cleaned_streams:
        stream_uuid = stream.get("id")
        cam_id = stream["camera_id"]
        full_key = f"{cam_id}|{stream_uuid}"
        reg = stream_registry.get(full_key, {})

        result.append({
            "id": stream_uuid,
            "camera_id": cam_id,
            "port": stream.get("port", reg.get("port")),
            "flask_port": stream.get("flask_port", reg.get("flask_port")),
            "model": reg.get("model", "Unknown"),
            "source": reg.get("source", "Unknown"),
            "feed_type": stream.get("feed_type", "video")
        })

        # result.append({
        #     "id": stream_uuid,
        #     "camera_id": cam_id,
        #     "port": stream.get("port", reg.get("port")),
        #     "model": reg.get("model", "Unknown"),
        #     "source": reg.get("source", "Unknown"),
        #     "feed_type": stream.get("feed_type", "video")
        # })

    return jsonify(result)



# @stream_control_bp.route('/api/streams', methods=['GET'])
# def get_active_streams():
#     session_streams = session.get("active_streams", [])
#     cleaned_streams = []

#     for stream in session_streams:
#         cam_id = stream.get("camera_id")
#         reg = stream_registry.get(cam_id)
#         if reg:
#             cleaned_streams.append(stream)

#     session["active_streams"] = cleaned_streams
#     session.modified = True

#     result = []
#     for stream in cleaned_streams:
#         stream_uuid = stream.get("id")
#         if not stream_uuid:
#             print(f"[ERROR] Stream entry missing UUID: {stream}")
#             continue  # Skip corrupted session entries

#         cam_id = stream["camera_id"]
#         reg = stream_registry.get(cam_id, {})

#         result.append({
#             "id": stream["id"],
#             "camera_id": cam_id,
#             "port": stream.get("port", reg.get("port")),
#             "model": reg.get("model", "Unknown"),
#             "source": reg.get("source", "Unknown"),
#             "feed_type": stream.get("feed_type", "video")
#         })

#     return jsonify(result)


# @stream_control_bp.route('/api/streams', methods=['GET'])
# def get_active_streams():
#     session_streams = session.get("active_streams", [])
#     cleaned_streams = []

#     for stream in session_streams:
#         cam_id = stream["camera_id"]
#         reg = stream_registry.get(cam_id)
#         if reg:
#             cleaned_streams.append(stream)

#     session["active_streams"] = cleaned_streams
#     session.modified = True

#     result = []
#     for stream in cleaned_streams:
#         cam_id = stream["camera_id"]
#         # reg = stream_registry[cam_id]
#         reg = stream_registry.get(cam_id, {})

#         result.append({
#             "id": stream["id"],
#             "camera_id": cam_id,
#             "port": stream.get("port", reg.get("port")),
#             "model": reg.get("model", "Unknown"),
#             "source": reg.get("source", "Unknown"),
#             "feed_type": stream.get("feed_type", "video")
#         })

#     return jsonify(result)



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

    # port = get_free_port()
    port_zmq = get_free_port()
    port_flask = get_free_port(start=5655)

    stream_uuid = uuid.uuid4().hex
    camera_arg = f"{camera_id}|{stream_uuid}"

    cmd = [
        "python3",
        os.path.join(BASE_DIR, "vehicle_tracking", "stream_feeder", "stream_feeder.py"),
        "--source", source,
        "--camera-id", camera_arg,
        "--connect-to", f"tcp://127.0.0.1:{port_zmq}",
        "--model-path", model_path,
        "--loop",
        "--flask-port", str(port_flask)
    ]

    print(f"[DEBUG] Launching stream: {cmd}")
    proc = subprocess.Popen(cmd)

    active_streams = session.get("active_streams", [])
    active_streams.append({
        "id": stream_uuid,
        "camera_id": camera_id,
        "feed_type": feed_type,
        "port": port_zmq,
        "flask_port": port_flask
    })
    session["active_streams"] = active_streams
    session.modified = True

    stream_registry[f"{camera_id}|{stream_uuid}"] = {
        "pid": proc.pid,
        "port": port_zmq,
        "flask_port": port_flask,
        "model": model_path,
        "source": source,
    }
    # stream_registry[f"{camera_id}|{stream_uuid}"] = {
    #     "pid": proc.pid,
    #     "port": port,
    #     "model": model_path,
    #     "source": source,
    # }


    return redirect(url_for('ui_routes.index'))


# @stream_control_bp.route('/stop_stream/<camera_id>', methods=['POST'])
# def stop_stream(camera_id):
#     print(f"[CONTROL] Attempting to stop stream: {camera_id}")

#     for proc in psutil.process_iter(['pid', 'cmdline']):
#         try:
#             cmdline = proc.info['cmdline']
#             if cmdline and camera_id in ' '.join(cmdline) and 'stream_feeder.py' in cmdline:
#                 print(f"[KILL] Found process for {camera_id}: PID={proc.pid}")
#                 proc.kill()

#                 # Remove from registry
#                 stream_registry.pop(camera_id, None)

#                 return f"Stream for {camera_id} stopped.", 200
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue

#     return f"No active stream found for {camera_id}.", 404


# @stream_control_bp.route('/stop_stream/<camera_id>', methods=['POST'])
# def stop_stream(camera_id):
#     camera_id = unquote(camera_id)
#     print(f"[CONTROL] Attempting to stop stream: {camera_id}")

#     try:
#         stream_info = stream_registry[camera_id]
#         pid = stream_info.get("pid")
#         if pid:
#             try:
#                 os.kill(pid, signal.SIGTERM)
#                 print(f"[CONTROL] Sent SIGTERM to PID {pid}")
#             except ProcessLookupError:
#                 print(f"[CONTROL] PID {pid} already terminated")

#         stream_registry.pop(camera_id, None)
#         active_streams = session.get("active_streams", [])
#         session["active_streams"] = [s for s in active_streams if s["camera_id"] != camera_id]
#         session.modified = True

#         return redirect(url_for('ui_routes.index'))

#     except KeyError:
#         print(f"[CONTROL] Camera ID not found: {camera_id}")
#         abort(404)
#     except Exception as e:
#         print(f"[CONTROL] Failed to stop stream {camera_id}: {e}")
#         abort(500)

# @stream_control_bp.route('/stop_stream/<camera_id>', methods=['POST'])
# def stop_stream(camera_id):
#     from urllib.parse import unquote
#     import signal
#     from flask import abort

#     camera_id = unquote(camera_id)
#     print(f"[CONTROL] Attempting to stop stream: {camera_id}")
#     print(f"[CONTROL] Available keys: {list(stream_registry.keys())}")

#     try:
#         stream_info = stream_registry[camera_id]
#         print(f"[CONTROL] Stream contents: {stream_info}")
#         pid = stream_info.get("pid")

#         if pid:
#             try:
#                 os.kill(pid, signal.SIGTERM)
#                 print(f"[CONTROL] Sent SIGTERM to PID {pid}")
#             except ProcessLookupError:
#                 print(f"[CONTROL] Process with PID {pid} does not exist (already stopped?)")

#         # Remove from registry and session
#         stream_registry.pop(camera_id, None)

#         active_streams = session.get("active_streams", [])
#         active_streams = [s for s in active_streams if s["camera_id"] != camera_id]
#         session["active_streams"] = active_streams
#         session.modified = True

#         print(f"[CONTROL] Successfully stopped and removed stream: {camera_id}")
#         return redirect(url_for('ui_routes.index'))

#     except KeyError:
#         print(f"[CONTROL] Camera ID not found in registry: {camera_id}")
#         abort(404)
#     except Exception as e:
#         print(f"[CONTROL] Failed to stop stream {camera_id}: {e}")
#         abort(500)

@stream_control_bp.route('/stop_stream/<camera_id>', methods=['POST'])
def stop_stream(camera_id):
    from urllib.parse import unquote
    import signal
    from flask import abort

    camera_id = unquote(camera_id)
    print(f"[CONTROL] Attempting to stop stream: {camera_id}")
    print(f"[CONTROL] Available keys: {list(stream_registry.keys())}")

    try:
        stream_info = stream_registry[camera_id]
        print(f"[CONTROL] Stream contents: {stream_info}")
        pid = stream_info.get("pid")

        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"[CONTROL] Sent SIGTERM to PID {pid}")
            except ProcessLookupError:
                print(f"[CONTROL] Process with PID {pid} does not exist (already stopped?)")

        # Remove from registry
        stream_registry.pop(camera_id, None)

        # Remove matching entry from session (by both base_cam_id and UUID)
        base_cam_id, _uuid = camera_id.split("|", 1)
        active_streams = session.get("active_streams", [])
        active_streams = [
            s for s in active_streams
            if not (s["camera_id"] == base_cam_id and s["id"] == _uuid)
        ]
        session["active_streams"] = active_streams
        session.modified = True

        print(f"[CONTROL] Successfully stopped and removed stream: {camera_id}")
        return redirect(url_for('ui_routes.index'))

    except KeyError:
        print(f"[CONTROL] Camera ID not found in registry: {camera_id}")
        abort(404)
    except Exception as e:
        print(f"[CONTROL] Failed to stop stream {camera_id}: {e}")
        abort(500)


# --------------


# -
#  @stream_control_bp.route('/add_stream', methods=['GET', 'POST'])
#  def add_stream():
#      if request.method == 'GET':
#          existing_videos = glob.glob("video_data/videos/*.mp4")
#          print("[DEBUG] Found videos:", existing_videos)
# -
#          return render_template('add_stream.html', existing_videos=existing_videos)

#      # POST logic
#      feed_type = request.form.get('feed_type')
# -
#      base_name = "Camera"
# -    i = 0
# +    i = 1
#      camera_id = f"{base_name} {i}"
#      while camera_id in stream_registry:
#          i += 1
#          camera_id = f"{base_name} {i}"

# -    port = get_free_port()
#      model_path = request.form.get("model_path")
#      session['selected_model'] = model_path
#      source = None
# @@ -108,7 +155,6 @@ def add_stream():
#              source = request.form.get('existing_file')
#          else:
#              return "No video file uploaded or selected", 400
# -
#      elif feed_type == 'rtsp':
#          source = request.form.get('rtsp_url')
#          if not source:
# @@ -130,9 +176,14 @@ def add_stream():
#      print(f"[DEBUG] Launching stream: {cmd}")
#      proc = subprocess.Popen(cmd)

# +    # Generate a UUID for this stream
# +    stream_uuid = uuid.uuid4().hex
# +    print(f"Creating Stream ID: {stream_uuid} for camera: {camera_id}")
# +
# +    # Save in session
#      active_streams = session.get("active_streams", [])
#      active_streams.append({
# -        "id": len(active_streams),
# +        "id": stream_uuid,
#          "camera_id": camera_id,
#          "feed_type": feed_type,
#          "port": port
# @@ -140,6 +191,7 @@ def add_stream():
#      session["active_streams"] = active_streams
#      session.modified = True

# +    # Register process in memory
#      stream_registry[camera_id] = {
#          "pid": proc.pid,
#          "port": port,
# @@ -151,23 +203,122 @@ def add_stream():



# @stream_control_bp.route('/add_stream', methods=['GET', 'POST'])
# def add_stream():
#     if request.method == 'GET':
#         existing_videos = glob.glob("video_data/videos/*.mp4")
#         print("[DEBUG] Found videos:", existing_videos)
#         return render_template('add_stream.html', existing_videos=existing_videos)

#     # POST logic
#     feed_type = request.form.get('feed_type')

#     base_name = "Camera"
#     i = 1
#     camera_id = f"{base_name} {i}"
#     while camera_id in stream_registry:
#         i += 1
#         camera_id = f"{base_name} {i}"
#     port = get_free_port()
#     model_path = request.form.get("model_path")
#     session['selected_model'] = model_path
#     source = None

#     print(f"[DEBUG] Selected model path: {model_path}")
#     print(f"[DEBUG] Feed type: {feed_type}")

#     if feed_type == 'video':
#         if 'video_file' in request.files and request.files['video_file'].filename:
#             video_file = request.files['video_file']
#             filename = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}.mp4")
#             video_file.save(filename)
#             source = filename
#         elif request.form.get('existing_file'):
#             source = request.form.get('existing_file')
#         else:
#             return "No video file uploaded or selected", 400

#     elif feed_type == 'rtsp':
#         source = request.form.get('rtsp_url')
#         if not source:
#             return "RTSP URL is required", 400
#     else:
#         return "Invalid feed type", 400

#     port = get_free_port()
#     cmd = [
#         "python3",
#         os.path.join(BASE_DIR, "vehicle_tracking", "stream_feeder", "stream_feeder.py"),
#         "--source", source,
#         "--camera-id", camera_id,
#         "--connect-to", f"tcp://127.0.0.1:{port}",
#         "--model-path", model_path,
#         "--loop"
#     ]

#     print(f"[DEBUG] Launching stream: {cmd}")
#     proc = subprocess.Popen(cmd)
#     active_streams = session.get("active_streams", [])

#     stream_id = str(uuid.uuid4())
#     print(f"Creating Stream ID: {stream_id} for camera: {camera_id}")

#     active_streams.append({
#         "id": uuid.uuid4().hex,
#         "camera_id": camera_id,
#         "feed_type": feed_type,
#         "port": port
#     })
#     session["active_streams"] = active_streams
#     session.modified = True

#     stream_registry[camera_id] = {
#         "pid": proc.pid,
#         "port": port,
#         "model": model_path,
#         "source": source,
#     }

#     return redirect(url_for('ui_routes.index'))
