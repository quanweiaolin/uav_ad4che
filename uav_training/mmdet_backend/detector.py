import os
import numpy as np
import torch
from mmengine.config import Config
from mmdet.registry import MODELS
from mmengine.runner import load_checkpoint
from mmengine.dataset import Compose
from copy import deepcopy

from mmrotate.utils import register_all_modules
register_all_modules()



def init_detector(config, checkpoint, device):
    cfg = Config.fromfile(config)

    cfg.custom_imports = dict(
        imports=[
            'mmdet.datasets.transforms',
            'mmrotate.datasets.transforms'
        ],
        allow_failed_imports=False
    )

    model = MODELS.build(cfg.model)
    load_checkpoint(model, checkpoint, map_location=device)
    model.to(device)
    model.eval()
    test_pipeline_cfg = deepcopy(cfg.test_dataloader.dataset.pipeline)

    test_pipeline_cfg[0] = dict(type='mmdet.LoadImageFromNDArray')

    test_pipeline_cfg = [
        p for p in test_pipeline_cfg
        if p['type'] not in ['LoadAnnotations', 'ConvertBoxType']
    ]

    test_pipeline = Compose(test_pipeline_cfg)
    return model, test_pipeline


class MMRotateDetector:
    def __init__(self, device="cuda:0"):
        BASE_DIR = os.path.dirname(__file__)

        config = os.path.join(
            BASE_DIR,
            "configs/oriented_rcnn/oriented-rcnn-le90_r50_fpn_1x_dota.py"
        )
        checkpoint = os.path.join(
            BASE_DIR,
            "checkpoints/oriented_rcnn_r50_fpn_1x_dota_le90-6d2b2ce0.pth"
        )

        self.device = device  # ⭐ 必须保存
        self.model, self.pipeline = init_detector(config, checkpoint, device=device)

    def infer(self, image: np.ndarray, score_thr=0.4):
        """返回旋转框检测结果"""

        data = dict(img=image, img_id=0)
        data = self.pipeline(data)

        data['inputs'] = data['inputs'].unsqueeze(0).to(self.device)
        data['data_samples'] = [data['data_samples']]

        with torch.no_grad():
            result = self.model.test_step(data)[0]  # DetDataSample

        pred = result.pred_instances  # ⭐ MMDet3 标准结构

        bboxes = pred.bboxes.detach().cpu().numpy()      # (N, 5)  cx,cy,w,h,angle
        scores = pred.scores.detach().cpu().numpy()      # (N,)
        labels = pred.labels.detach().cpu().numpy()      # (N,)

        detections = []
        for bbox, score, label in zip(bboxes, scores, labels):
            if score < score_thr:
                continue

            cx, cy, w, h, angle = bbox.tolist()

            detections.append({
                "cx": cx,
                "cy": cy,
                "w": w,
                "h": h,
                "angle": angle,
                "score": float(score),
                "label": int(label),
            })

        return detections
