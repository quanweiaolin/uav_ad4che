import os
import cv2 as cv
import numpy as np
from time import time
from tqdm import tqdm
from uav_pipeline.stages.stabilization.algorithms.stabilization_tools import *

class VideoStabilizerV3:
    def __init__(
        self,
        input_video_path,
        output_video_path,
        mask_img_path=None,
        reference_frame_path=None,
        params=None,
    ):
        self.input_video_path = input_video_path
        self.output_video_path = output_video_path
        self.mask_img_path = mask_img_path
        self.reference_frame_path = reference_frame_path

        p = params or {}

        self.downsample_ratio = p.get("downsample_ratio", 0.5)
        self.harris_response_thresh = p.get("harris_response_thresh", 0.08)
        self.harris_response_thresh_align = p.get("harris_response_thresh_align", 0.07)
        self.filter_ratio = p.get("filter_ratio", 0.8)

        self.ransac_method = cv.USAC_MAGSAC
        self.ransac_reproj_thresh = p.get("ransac_reproj_thresh", 2.0)
        self.ransac_max_iter = p.get("ransac_max_iter", 5000)
        self.ransac_confidence = p.get("ransac_confidence", 0.999999)

        self.descriptor = cv.ORB_create()
        self.matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=False)

        self.ref_frame = None
        self.ref_gray = None
        self.ref_kp = None
        self.ref_des = None

        self.mask = None
        self.height = None
        self.width = None

        self.H0 = np.eye(3) # if no ref img

    def align_compute(self):
        if self.reference_frame_path is None:
            return np.eye(3)

        base_frame = cv.imread(self.reference_frame_path)
        base_gray = preprocess_frame(base_frame, 1.0)
        first_gray = preprocess_frame(self.ref_frame, 1.0)

        base_kp = harris_corner_detect(base_gray, None, response_thresh=self.harris_response_thresh_align)
        first_kp = harris_corner_detect(first_gray, None, response_thresh=self.harris_response_thresh_align)

        base_kp, base_des = self.descriptor.compute(base_gray, base_kp)
        first_kp, first_des = self.descriptor.compute(first_gray, first_kp)

        matches = match_features(base_des, first_des, self.matcher, self.filter_ratio)

        H0, _ = compute_transform(
            base_kp, first_kp, matches,
            self.ransac_method,
            self.ransac_reproj_thresh,
            self.ransac_max_iter,
            self.ransac_confidence
        )
        return H0

    # ===== 单帧处理（完全保留你逻辑）=====
    def single_frame(self, frame):

        if self.height is None:
            self.height, self.width = frame.shape[:2]

        if self.mask is None:
            if self.mask_img_path and os.path.exists(self.mask_img_path):
                mask = image_mask(self.mask_img_path, self.width, self.height)
            else:
                mask = np.ones((self.height, self.width), dtype=np.uint8) * 255
            self.mask = downsample_frame(mask, self.downsample_ratio)

        if self.ref_frame is None:
            self.ref_frame = frame.copy()
            self.ref_gray = preprocess_frame(self.ref_frame, self.downsample_ratio)
            self.ref_kp = harris_corner_detect(self.ref_gray, self.mask, response_thresh=self.harris_response_thresh)
            self.ref_kp, self.ref_des = self.descriptor.compute(self.ref_gray, self.ref_kp)
            self.H0 = self.align_compute()
            return frame, 0, 0, 0

        curr_gray = preprocess_frame(frame, self.downsample_ratio)
        curr_kp = harris_corner_detect(curr_gray, self.mask, response_thresh=self.harris_response_thresh)
        curr_kp, curr_des = self.descriptor.compute(curr_gray, curr_kp)

        matches = match_features(self.ref_des, curr_des, self.matcher, self.filter_ratio)

        H_lowres, inliers_count = compute_transform(
            self.ref_kp, curr_kp, matches,
            self.ransac_method,
            self.ransac_reproj_thresh,
            self.ransac_max_iter,
            self.ransac_confidence
        )

        H = scale_homography_matrix(H_lowres, self.downsample_ratio)
        stabilized_frame = cv.warpPerspective(frame, H, (self.width, self.height))
        return stabilized_frame, inliers_count, len(matches), len(curr_kp)

    def stabilize(self):
        os.makedirs(os.path.dirname(self.output_video_path), exist_ok=True)
        
        cap = cv.VideoCapture(self.input_video_path)
        fps = cap.get(cv.CAP_PROP_FPS)
        self.width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(self.output_video_path, fourcc, fps, (self.width, self.height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            stabilized_frame, *_ = self.single_frame(frame)
            aligned_frame = cv.warpPerspective(stabilized_frame, self.H0, (self.width, self.height))
            out.write(aligned_frame)

        cap.release()
        out.release()