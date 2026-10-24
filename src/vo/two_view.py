import cv2
import numpy as np


def matched_points(keypoints_a, keypoints_b, matches):
    points_a = np.float32([keypoints_a[m.queryIdx].pt for m in matches])
    points_b = np.float32([keypoints_b[m.trainIdx].pt for m in matches])
    return points_a, points_b


def estimate_relative_pose(points_a, points_b, K):
    E, mask = cv2.findEssentialMat(
        points_a,
        points_b,
        K,
        method=cv2.RANSAC,
        prob=0.999,
        threshold=1.0,
    )
    if E is None:
        raise RuntimeError("Essential matrix estimation failed")

    _, R, t, pose_mask = cv2.recoverPose(E, points_a, points_b, K, mask=mask)
    inlier_count = int(np.count_nonzero(pose_mask))
    return R, t.reshape(3), inlier_count

