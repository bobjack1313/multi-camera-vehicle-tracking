# vehicle_tracking/utils/stream_registry.py

# Global in-memory registry for active camera stream configurations.
# This gets populated during stream creation (e.g., add_stream).
stream_registry = {}