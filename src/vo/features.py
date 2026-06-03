import cv2


def create_orb(max_features: int = 2500):
    return cv2.ORB_create(nfeatures=max_features)


def detect_and_compute(orb, image):
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return keypoints, descriptors


def match_descriptors(desc_a, desc_b):
    if desc_a is None or desc_b is None:
        return []
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(desc_a, desc_b)
    return sorted(matches, key=lambda match: match.distance)

