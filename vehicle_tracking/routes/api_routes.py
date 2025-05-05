# multi-camera-vehicle-tracking
# api_routes.py
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

from flask import Blueprint, jsonify
from flask import send_file, abort
import os
import shutil
import tempfile
import io
import zipfile


api_bp = Blueprint('api_routes', __name__)

# You can prefix blueprints using:
# app.register_blueprint(api_bp, url_prefix='/api')

# # For now: a static test list (later replace with real stream tracking)
# streams = [
#     {"id": 0, "camera_id": "Camera 1", "feed_type": "yolo"},
#     {"id": 1, "camera_id": "Camera 2", "feed_type": "yolo"}
# ]

@api_bp.route('/api/status')
def system_status():
    return jsonify({"status": "ok", "message": "API is running"})


@api_bp.route('/api/streams')
def get_streams():
    active_streams = session.get("active_streams", [])
    return jsonify(active_streams)



# @api_bp.route('/export_logs/<date_str>', methods=['GET'])
# def export_logs_for_date(date_str):
#     base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
#     date_folder = os.path.join(base_dir, 'counts', date_str)

#     if not os.path.exists(date_folder):
#         abort(404, description=f"No logs found for {date_str}")

#     with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
#         shutil.make_archive(temp_zip.name[:-4], 'zip', date_folder)
#         zip_path = temp_zip.name

#     return send_file(zip_path, as_attachment=True, download_name=f"vehicle_logs_{date_str}.zip")


@api_bp.route("/api/log_dates")
def get_all_log_dates():
    import os
    from flask import jsonify
    from datetime import datetime

    log_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../counts"))


    if not os.path.exists(log_base):
        return jsonify([])

    folders = [
        name for name in os.listdir(log_base)
        if os.path.isdir(os.path.join(log_base, name))
    ]

    # Format dates
    results = []
    for folder in folders:
        try:
            dt = datetime.strptime(folder, "%Y-%m-%d")
            label = dt.strftime("%B %d, %Y")  # e.g. "March 25, 2025"
        except ValueError:
            label = folder  # fallback if not a date
        results.append({"folder": folder, "label": label})

    return jsonify(sorted(results, key=lambda x: x["folder"]))



COUNTS_DIR = os.path.join(os.path.dirname(__file__), "..", "counts")

@api_bp.route("/export_logs/<date_str>", methods=["GET"])
def export_logs_by_date(date_str):
    folder_path = os.path.join(COUNTS_DIR, date_str)
    if not os.path.exists(folder_path):
        return f"No logs found for date: {date_str}", 404

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, COUNTS_DIR)
                zipf.write(file_path, arcname)

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name=f"{date_str}_logs.zip")


@api_bp.route("/export_logs_all", methods=["GET"])
def export_all_logs():
    if not os.path.exists(COUNTS_DIR):
        return "Counts folder not found", 404

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(COUNTS_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, COUNTS_DIR)
                zipf.write(file_path, arcname)

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="all_logs.zip")



