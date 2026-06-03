# visual-slam-lab

Monocular visual odometry and SLAM study repo.

The first milestone is a small KITTI odometry pipeline:

1. Load calibrated image sequences.
2. Detect ORB features.
3. Match descriptors between consecutive frames.
4. Estimate an essential matrix.
5. Recover relative camera pose.
6. Accumulate and plot a trajectory.

This repo intentionally starts with Python and OpenCV so the geometry is easy to inspect before moving pieces to C++.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data

Download KITTI odometry sequence data from:

```text
https://www.cvlibs.net/datasets/kitti/eval_odometry.php
```

Place extracted data under:

```text
data/kitti/dataset/
```

Expected layout:

```text
data/kitti/dataset/
  sequences/
    00/
      image_0/
      calib.txt
  poses/
    00.txt
```

## First Run

```bash
python -m src.vo.run_kitti --sequence 00 --max-frames 200
```

