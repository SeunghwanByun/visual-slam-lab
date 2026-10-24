# Local KITTI data

Verified on 2026-10-23.

The code and VSCode launch configurations use `data/kitti/dataset`.
Sequences `00` through `21` now have real `image_0` and `image_1` directories:

```text
data/kitti/dataset/sequences/<sequence>/image_<camera>
```

Images were moved into the repository. No Downloads dependency remains.
The three Downloads dataset folders and all three original ZIPs were removed.
The repository's redundant `data/downloads` archives were also removed.
The inventory below records the locations before consolidation.

Local inventory:

| Location | Contents |
| --- | --- |
| `~/Downloads/dataset` | Calibration and timestamps; identical to repo copies |
| `~/Downloads/dataset 2` | Ground truth poses; identical to repo copies |
| `~/Downloads/dataset 3` | Grayscale stereo images, about 22 GiB |
| `~/Downloads/data_odometry_gray.zip` | Original image archive, about 22 GiB |
| `data/kitti/dataset` | Existing metadata plus image symlinks |
| `data/downloads/kitti` | Previously downloaded calibration and pose archives |

The home-directory search found no other extracted image dataset. It excluded
Library, caches, virtual environments, node_modules and .git; inaccessible
locations were not checked. No external volume was mounted.

Run from the repository root:

```bash
.venv/bin/python scripts/check_kitti_dataset.py --sequence 00
.venv/bin/python -m src.vo.run_kitti --sequence 00 --max-frames 50
```
