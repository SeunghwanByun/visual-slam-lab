from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_trajectory(estimated: np.ndarray, ground_truth: np.ndarray | None, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))
    plt.plot(estimated[:, 0], estimated[:, 2], label="estimated", linewidth=1.5)

    if ground_truth is not None:
        gt_xyz = ground_truth[:, :, 3]
        plt.plot(gt_xyz[:, 0], gt_xyz[:, 2], label="ground truth", linewidth=1.5)

    plt.axis("equal")
    plt.xlabel("x")
    plt.ylabel("z")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

