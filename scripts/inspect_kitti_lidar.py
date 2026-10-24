import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_velodyne_scan(path: Path) -> np.ndarray:
    points = np.fromfile(path, dtype=np.float32)
    if points.size % 4 != 0:
        raise RuntimeError(f"Invalid KITTI Velodyne scan: {path}")
    return points.reshape(-1, 4)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data/kitti/dataset"))
    parser.add_argument("--sequence", default="00")
    parser.add_argument("--frame", type=int, default=0)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--max-range", type=float, default=60.0)
    args = parser.parse_args()

    scan_path = (
        args.data_root
        / "sequences"
        / args.sequence
        / "velodyne"
        / f"{args.frame:06d}.bin"
    )
    if not scan_path.exists():
        raise FileNotFoundError(f"Missing Velodyne scan: {scan_path}")

    points = load_velodyne_scan(scan_path)
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    intensity = points[:, 3]

    mask = (
        (x > 0.0)
        & (np.abs(x) < args.max_range)
        & (np.abs(y) < args.max_range)
        & (z > -3.0)
        & (z < 3.0)
    )

    output_path = args.output or Path("outputs") / f"kitti_{args.sequence}_lidar_{args.frame:06d}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 8))
    plt.scatter(
        x[mask],
        y[mask],
        c=intensity[mask],
        s=0.2,
        cmap="viridis",
        linewidths=0,
    )
    plt.axis("equal")
    plt.xlabel("forward x")
    plt.ylabel("left y")
    plt.title(f"KITTI {args.sequence} Velodyne frame {args.frame:06d}")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()

    print(f"points={points.shape[0]}")
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
