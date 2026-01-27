import numpy as np
import cv2 as cv

def compute_homography(kp1, kp2, matches, ransac_thresh=5.0, max_iter=5000, confidence=0.999):
    if len(matches) < 4:
        return np.eye(3), 0
    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
    H, mask = cv.findHomography(pts2, pts1, cv.USAC_MAGSAC, ransac_thresh, maxIters=max_iter, confidence=confidence)
    inliers = np.count_nonzero(mask) if mask is not None else 0
    return H if H is not None else np.eye(3), inliers