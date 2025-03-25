<h1 align='center'>
Convert DETRAC Dataset for YOLO and Deep SORT
</h1>

# Convert DETRAC Dataset for YOLOv8 and (Optional) Deep SORT Appearance Model

This toolset allows you to prepare the DETRAC vehicle dataset for use with modern object detection and tracking workflows, specifically:

- **YOLOv8** (Ultralytics PyTorch-based)
- **Deep SORT** (appearance-based tracking, optional)

Previous Notes:
I followed this [paper](https://ieeexplore.ieee.org/document/8909903) as a guideline for parameters. They removed all sequences of vehicles that had a truncation or occlusion threshold higher than 0.5. Those that then had less than 100 occurrences were ignored. Each vehicle in each satisfactory image is then cropped and resized to 100x100.

I've replicated that in the script so that you can choose your own thresholds and output image size. The script basically goes through the annotations and creates a dictionary of what to crop and what to ignore.

The cropped sequences should all be outputted to the `DETRAC_cropped` directory in Market 1501 format. Then, follow the instructions on how to train a Market 1501 dataset in the njojke's [cosine metric learning](https://github.com/nwojke/cosine_metric_learning) repository.

---

## Tools Included

### 1. `detrac_to_yolo.py`
Converts DETRAC annotations to **YOLOv8-compatible format**.

- Outputs training images and YOLO `.txt` labels
- Applies optional occlusion and truncation filters
- Saves images to `DETRAC_YOLO_training/`
- Saves annotations to `DETRAC_YOLO_annotations/`
- Generates `detrac_classes.txt` to list classes used

**Example usage:**
```bash
python detrac_to_yolo.py --occlusion_threshold=0.6 --truncation_threshold=0.6
```

### Parameters:
- `--occlusion_threshold`: Minimum allowed occlusion ratio (default: 0.5)
- `--truncation_threshold`: Minimum allowed truncation ratio (default: 0.5)

The output can be used directly to train a YOLOv8 model with:
```bash
yolo detect train \
  data=datasets/detrac_yolo/data.yaml \
  model=yolov8n.pt \
  epochs=50
```

---

### 2. `crop_dataset.py` *(Optional)*
Used to prepare vehicle crops in **Market-1501 format** for training a **Deep SORT re-ID model** (if you are not using `deep_sort_realtime`).

- Filters sequences with heavy occlusion or truncation
- Ignores vehicle IDs with fewer than X appearances
- Outputs cropped images to `DETRAC_cropped/`

**Example usage:**
```bash
python crop_dataset.py --occlusion_threshold=0.6 --truncation_threshold=0.6 --occurrences=50
```

**Default values:**
- `occlusion_threshold = 0.5`
- `truncation_threshold = 0.5`
- `occurrences = 100`
- `image_size = 100x100`

> You can use this output with projects that follow Market-1501 style training (e.g., cosine metric learning for appearance embedding).

---

## Dataset Info
Using the default DETRAC training split:
- ~163,000 cropped images for Deep SORT
- ~81,000 annotated images for YOLO training

These will require approx. **5GB+ of space** during conversion.

---

## Credits
- DETRAC Dataset: [http://detrac-db.rit.albany.edu](http://detrac-db.rit.albany.edu)
- Based on conversion logic inspired by [this paper](https://ieeexplore.ieee.org/document/8909903)
- YOLOv8: [https://github.com/ultralytics/ultralytics](https://github.com/ultralytics/ultralytics)
- Deep SORT re-ID: [https://github.com/nwojke/cosine_metric_learning](https://github.com/nwojke/cosine_metric_learning)
