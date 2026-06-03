import argparse
from pathlib import Path

import numpy as np

from src.datasets.kitti import KittiSequence
from src.viz.plot_trajectory import plot_trajectory
from src.vo.features import create_orb, detect_and_compute, match_descriptors
from src.vo.two_view import estimate_relative_pose, matched_points


def run(sequence: str, data_root: Path, max_frames: int):
    dataset = KittiSequence(data_root, sequence)
    frame_count = min(len(dataset), max_frames)
    if frame_count < 2:
        raise RuntimeError("Need at least two frames")

    orb = create_orb()
    current_pose = np.eye(4)
    trajectory = [current_pose[:3, 3].copy()]

    prev_image = dataset.read_gray(0)
    prev_kp, prev_desc = detect_and_compute(orb, prev_image)

    for index in range(1, frame_count):
        image = dataset.read_gray(index)
        keypoints, descriptors = detect_and_compute(orb, image)
        matches = match_descriptors(prev_desc, descriptors)[:1000]

        if len(matches) < 8:
            print(f"frame {index}: skipped, not enough matches")
            prev_kp, prev_desc = keypoints, descriptors
            continue

        points_a, points_b = matched_points(prev_kp, keypoints, matches)
        R, t, inliers = estimate_relative_pose(points_a, points_b, dataset.K)

        relative_pose = np.eye(4)
        relative_pose[:3, :3] = R
        relative_pose[:3, 3] = t

        current_pose = current_pose @ np.linalg.inv(relative_pose)
        trajectory.append(current_pose[:3, 3].copy())

        print(f"frame {index}: matches={len(matches)} inliers={inliers}")
        prev_kp, prev_desc = keypoints, descriptors

    estimated = np.array(trajectory)
    ground_truth = dataset.load_ground_truth()
    if ground_truth is not None:
        ground_truth = ground_truth[: len(estimated)]

    output_path = Path("outputs") / f"kitti_{sequence}_trajectory.png"
    plot_trajectory(estimated, ground_truth, output_path)
    print(f"wrote {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence", default="00")
    parser.add_argument("--data-root", type=Path, default=Path("data/kitti/dataset"))
    parser.add_argument("--max-frames", type=int, default=200)
    args = parser.parse_args()
    run(args.sequence, args.data_root, args.max_frames)


if __name__ == "__main__":
    main()

