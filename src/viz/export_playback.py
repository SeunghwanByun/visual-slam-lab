"""Export a self-contained, offline KITTI debugging playback."""

import argparse
import base64
import json
from pathlib import Path

import cv2
import numpy as np

from src.datasets.kitti import KittiSequence
from src.vo.features import create_orb, detect_and_compute, match_descriptors
from src.vo.two_view import matched_points


def export(root, sequence, max_frames, output):
    dataset = KittiSequence(root, sequence)
    count = min(len(dataset), max_frames)
    if count < 2:
        raise ValueError('At least two frames are required')
    times_path = dataset.sequence_dir / 'times.txt'
    times = np.loadtxt(times_path).reshape(-1) if times_path.exists() else None
    gt = dataset.load_ground_truth()
    orb = create_orb()
    pose = np.eye(4)
    frames = []
    previous_kp, previous_desc = None, None
    for index in range(count):
        gray = dataset.read_gray(index)
        kp, desc = detect_and_compute(orb, gray)
        tracks, status, inliers = [], 'initial', 0
        if index:
            matches = match_descriptors(previous_desc, desc)[:1000]
            status = 'insufficient matches'
            if len(matches) >= 8:
                a, b = matched_points(previous_kp, kp, matches)
                accepted = np.zeros(len(matches), dtype=bool)
                try:
                    essential, mask = cv2.findEssentialMat(
                        a, b, dataset.K, method=cv2.RANSAC, prob=0.999, threshold=1.0)
                    if essential is None:
                        raise ValueError('essential matrix failed')
                    _, rotation, translation, mask = cv2.recoverPose(
                        essential, a, b, dataset.K, mask=mask)
                    accepted = mask.reshape(-1) != 0
                    inliers = int(accepted.sum())
                    if inliers >= 5:
                        relative = np.eye(4)
                        relative[:3, :3] = rotation
                        relative[:3, 3] = translation.reshape(3)
                        pose = pose @ np.linalg.inv(relative)
                        status = 'tracked'
                    else:
                        status = 'pose rejected; position held'
                except (cv2.error, ValueError) as error:
                    status = f'pose failed; position held: {error}'
                tracks = [[*map(float, p), *map(float, q), bool(ok)]
                          for p, q, ok in zip(a, b, accepted)]
        ok, encoded = cv2.imencode('.jpg', gray, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ok:
            raise RuntimeError('JPEG encoding failed')
        frames.append(dict(
            image=base64.b64encode(encoded).decode('ascii'),
            points=[list(map(float, point.pt)) for point in kp],
            tracks=tracks, inliers=inliers, status=status,
            time=float(times[index]) if times is not None and index < len(times) else index / 10,
            vo=pose[:3, 3].tolist(),
            gt=gt[index, :, 3].tolist() if gt is not None and index < len(gt) else None))
        previous_kp, previous_desc = kp, desc
        if index % 25 == 0:
            print(f'Prepared {index + 1}/{count}', flush=True)
    payload = dict(sequence=sequence, width=gray.shape[1], height=gray.shape[0], frames=frames)
    template = Path(__file__).with_name('playback.html').read_text()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace('__PLAYBACK_DATA__', json.dumps(payload)), encoding='utf-8')
    print(f'Playback: {output.resolve()}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-root', type=Path, default=Path('data/kitti/dataset'))
    parser.add_argument('--sequence', default='00')
    parser.add_argument('--max-frames', type=int, default=200)
    parser.add_argument('--output', type=Path, default=Path('outputs/playback.html'))
    args = parser.parse_args()
    export(args.data_root, args.sequence, args.max_frames, args.output)


if __name__ == '__main__':
    main()
