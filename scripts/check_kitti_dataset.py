import argparse
from pathlib import Path

import cv2
import numpy as np


def count_files(path: Path, suffix: str) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.glob(f"*{suffix}"))


def print_status(label: str, ok: bool, detail: str) -> None:
    mark = "OK" if ok else "MISSING"
    print(f"[{mark}] {label}: {detail}")


def check_sequence(root: Path, sequence: str) -> int:
    sequence_dir = root / "sequences" / sequence
    image_0_dir = sequence_dir / "image_0"
    image_1_dir = sequence_dir / "image_1"
    velodyne_dir = sequence_dir / "velodyne"
    calib_path = sequence_dir / "calib.txt"
    times_path = sequence_dir / "times.txt"
    pose_path = root / "poses" / f"{sequence}.txt"

    failures = 0

    checks = [
        ("sequence directory", sequence_dir, sequence_dir.exists()),
        ("left grayscale camera image_0", image_0_dir, image_0_dir.exists()),
        ("right grayscale camera image_1", image_1_dir, image_1_dir.exists()),
        ("calibration", calib_path, calib_path.exists()),
        ("timestamps", times_path, times_path.exists()),
        ("ground truth poses", pose_path, pose_path.exists()),
    ]

    for label, path, ok in checks:
        print_status(label, ok, str(path))
        failures += 0 if ok else 1

    left_count = count_files(image_0_dir, ".png")
    right_count = count_files(image_1_dir, ".png")
    lidar_count = count_files(velodyne_dir, ".bin")

    print(f"image_0 frames: {left_count}")
    print(f"image_1 frames: {right_count}")
    print(f"velodyne scans: {lidar_count}")

    if left_count:
        first_image = next(iter(sorted(image_0_dir.glob("*.png"))))
        image = cv2.imread(str(first_image), cv2.IMREAD_GRAYSCALE)
        ok = image is not None
        print_status(
            "first image decode",
            ok,
            f"{first_image} shape={None if image is None else image.shape}",
        )
        failures += 0 if ok else 1

    if lidar_count:
        first_scan = next(iter(sorted(velodyne_dir.glob("*.bin"))))
        points = np.fromfile(first_scan, dtype=np.float32)
        ok = points.size % 4 == 0
        shape = (points.size // 4, 4) if ok else "invalid"
        print_status("first LiDAR scan decode", ok, f"{first_scan} shape={shape}")
        failures += 0 if ok else 1
    else:
        print_status("LiDAR scans", False, f"{velodyne_dir} (needed later for LiDAR SLAM)")

    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data/kitti/dataset"))
    parser.add_argument("--sequence", default="00")
    args = parser.parse_args()

    failures = check_sequence(args.data_root, args.sequence)
    if failures:
        raise SystemExit(f"KITTI dataset check failed with {failures} missing/invalid item(s)")
    print("KITTI dataset check passed")


if __name__ == "__main__":
    main()
