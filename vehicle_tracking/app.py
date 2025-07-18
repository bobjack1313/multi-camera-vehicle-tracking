# multi-camera-vehicle-tracking
# app.py
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

try:
    from routes.stream_control_routes import stream_control_bp
except Exception as e:
    import traceback
    print("[ERROR] Failed to import stream_control_bp:")
    traceback.print_exc()
    raise

from flask import Flask
from routes.ui_routes import ui_bp
from routes.stream_routes import stream_bp
#from routes.stream_control_routes import stream_control_bp
from routes.api_routes import api_bp
import os


def load_application_key(filename='application_validation.txt'):
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, filename)
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        raise RuntimeError(f"Failed to load secret key from {path}: {e}")


app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

app.secret = load_application_key()

# Register Blueprints
app.register_blueprint(ui_bp)
app.register_blueprint(stream_bp)
app.register_blueprint(stream_control_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
