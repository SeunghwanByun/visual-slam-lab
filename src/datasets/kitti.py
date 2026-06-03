from pathlib import Path

import cv2
import numpy as np


class KittiSequence:
    def __init__(self, root: Path, sequence: str):
        self.sequence = sequence
        self.sequence_dir = root / "sequences" / sequence
        self.image_dir = self.sequence_dir / "image_0"
        self.calib_path = self.sequence_dir / "calib.txt"
        self.pose_path = root / "poses" / f"{sequence}.txt"

        if not self.image_dir.exists():
            raise FileNotFoundError(f"Missing KITTI image directory: {self.image_dir}")
        if not self.calib_path.exists():
            raise FileNotFoundError(f"Missing KITTI calibration file: {self.calib_path}")

        self.image_paths = sorted(self.image_dir.glob("*.png"))
        self.K = self._load_camera_matrix()

    def __len__(self) -> int:
        return len(self.image_paths)

    def read_gray(self, index: int) -> np.ndarray:
        image = cv2.imread(str(self.image_paths[index]), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise RuntimeError(f"Failed to read image: {self.image_paths[index]}")
        return image

    def load_ground_truth(self) -> np.ndarray | None:
        if not self.pose_path.exists():
            return None
        poses = []
        with self.pose_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                values = np.fromstring(line, sep=" ", dtype=np.float64)
                poses.append(values.reshape(3, 4))
        return np.stack(poses)

    def _load_camera_matrix(self) -> np.ndarray:
        with self.calib_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("P0:"):
                    values = np.fromstring(line[3:], sep=" ", dtype=np.float64)
                    projection = values.reshape(3, 4)
                    return projection[:, :3]
        raise RuntimeError(f"P0 calibration not found in {self.calib_path}")

