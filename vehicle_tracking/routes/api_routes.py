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

api_bp = Blueprint('api_routes', __name__)

# You can prefix blueprints using:
# app.register_blueprint(api_bp, url_prefix='/api')

@api_bp.route('/api/status')
def system_status():
    return jsonify({"status": "ok", "message": "API is running"})