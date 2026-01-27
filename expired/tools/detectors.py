import cv2 as cv
import numpy as np
from abc import ABC, abstractmethod

class BaseDetector(ABC):
    # def __init__(self, cfg: dict = None):
    #     self.cfg = cfg or {}

    @abstractmethod
    def detect(self, frame):
        """return keypoints 和 descriptors"""
        pass


# ---------------- Harris ----------------
class HarrisDetector(BaseDetector):
    def __init__(self, 
                #  downsample_ratio, 
                 harris_response_thresh,
                 blockSize,
                 ksize,
                 k
                 ):
        self.downsample_ratio = downsample_ratio
        self.harris_response_thresh = harris_response_thresh
        self.blockSize = blockSize
        self.ksize = ksize
        self.k = k

        
    def detect(self, frame, mask=None):
        

        # 降采样 + 灰度化
        h, w = frame.shape[:2]
        new_w, new_h = int(w * self.downsample_ratio), int(h * self.downsample_ratio)
        frame_gray = cv.cvtColor(cv.resize(frame, (new_w, new_h)), cv.COLOR_BGR2GRAY)

        # Harris响应
        dst = cv.cornerHarris(frame_gray, blockSize=2, ksize=3, k=0.04)
        thresh = self.harris_response_thresh * dst.max()
        corners_yx = np.argwhere(dst > thresh)

        # 转成KeyPoint
        kp_list = [cv.KeyPoint(float(x), float(y), 31, -1) for y, x in corners_yx]

        # ORB描述符
        if kp_list:
            kp_list, des = cv.ORB_create().compute(frame_gray, kp_list)
        else:
            des = None
        return kp_list, des


# ---------------- SIFT ----------------
class SIFTDetector(BaseDetector):
    def detect(self, frame):
        """SIFT detector + des"""
        downsample_ratio = self.cfg.get("downsample_ratio", 1.0)  # no downsample
        n_features = self.cfg.get("n_features", 500)               # 500 features
        contrast_threshold = self.cfg.get("contrast_threshold", 0.04)
        edge_threshold = self.cfg.get("edge_threshold", 10)
        sigma = self.cfg.get("sigma", 1.6)

        
        h, w = frame.shape[:2]
        new_w, new_h = int(w * downsample_ratio), int(h * downsample_ratio)
        frame_gray = cv.cvtColor(cv.resize(frame, (new_w, new_h)), cv.COLOR_BGR2GRAY)

        
        sift = cv.SIFT_create(
            nfeatures=n_features,
            contrastThreshold=contrast_threshold,
            edgeThreshold=edge_threshold,
            sigma=sigma
        )
        kp_list, des = sift.detectAndCompute(frame_gray, mask=None)

        return kp_list, des