<h1 align='center'>
Multi-Camera Vehicle Tracking
</h1>

This repository contains an upgraded version of the original Multi-Camera Live Object Tracking system. It features modernized, GPU-accelerated real-time object detection and tracking using **YOLOv8**, **Deep SORT (PyTorch)**, and **Flask**. It supports live IP camera feeds, emulated streams, and video files, with customizable class-based object counting, tracking IDs, and CSV logging.

> This project was originally forked from [LeonLok’s Multi-Camera Live Object Tracking](https://github.com/LeonLok/Multi-Camera-Live-Object-Tracking) and has since been restructured, refactored, and upgraded for modern deployment and extensibility under the terms of the GPLv3 License.

---

##Key Features

- **YOLOv8 object detection** with custom-trained models
- **Deep SORT object tracking** rewritten in PyTorch
- **Multi-camera support** with async streaming via ImageZMQ
- **Accurate vehicle counting** with directional analysis
- **Real-time Flask web dashboard**
- **Custom training pipeline** using Roboflow, DETRAC, or your own data
- **CSV export** for:
  - Total counts
  - Class-based counts
  - Intersection metadata (angle, time, coordinate)

---

##Use Cases
- Traffic analytics for smart cities
- Entry/exit flow monitoring
- Parking lot analysis
- Multi-zone object tracking

---

##How It Works

1. **Streams** are received from local videos, IP cameras, or smartphones (via [ImageZMQ](https://github.com/jeffbass/imagezmq))
2. **YOLOv8** detects objects per frame (custom or COCO weights supported)
3. **Deep SORT** assigns tracking IDs across frames
4. **Counting logic** determines intersections across defined lines and tracks movement direction
5. **Flask app** streams all camera feeds to the browser with real-time overlays

---

##Training Custom Models
We support:
- Uploading and labeling your own data via [Roboflow](https://roboflow.com)
- Conversion of public datasets (e.g. DETRAC) using built-in tools

Custom models are trained using:
```bash
yolo detect train \
  data=datasets/your_dataset/data.yaml \
  model=yolov8n.pt \
  imgsz=640 \
  epochs=50 \
  batch=16 \
  name=custom_model
```

---

##Recommended Hardware
- **GPU:** NVIDIA GTX 1650 or better
- **CPU:** Quad-core or higher
- **RAM:** 8GB minimum
- Originally deployed on Ubuntu 24.04

---

##Dependencies
- Python 3.10+
- PyTorch (with CUDA support)
- Ultralytics (YOLOv8)
- OpenCV
- Flask
- ImageZMQ

Use the provided `environment.yml` to set up your conda environment:
```bash
conda env create -f environment.yml
conda activate multi_cam_v2
```

---

##Sample Output
<div align='center'>
<img src="gifs/traffic_counting1.gif" width="80%"/>
</div>

---

##License

This project is licensed under the terms of the **GNU General Public License v3.0 (GPL-3.0)**.

You are free to:
- Use, modify, and distribute this software under the same GPLv3 terms.
- Build upon the work, but **must also license your derivative works under GPLv3**.

See the full license text in the [LICENSE](./LICENSE) file or visit [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html) for more information.

---

##Credits
- [LeonLok](https://github.com/LeonLok) - Original Deep SORT + YOLOv4 implementation
- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLOv8 engine
- [deep_sort_realtime](https://github.com/mikel-brostrom/Yolov5_DeepSort_Pytorch)
- [Jeff Bass](https://github.com/jeffbass/imagezmq) - ImageZMQ
- [Miguel Grinberg](https://github.com/miguelgrinberg/flask-video-streaming) - Flask streaming base
