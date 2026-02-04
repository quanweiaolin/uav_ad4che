from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
import numpy as np
import cv2 as cv
from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class Obj:
    # --- detection level ---
    label: int
    score: float

    cx: float
    cy: float
    w: float
    h: float
    angle: float

    # # --- tracking level ---
    # track_id: Optional[int] = None
    # vx: Optional[float] = None
    # vy: Optional[float] = None

    # # --- refinement level ---
    # wx: Optional[float] = None
    # wy: Optional[float] = None
    # wz: Optional[float] = None
    # world_vx: Optional[float] = None
    # world_vy: Optional[float] = None

    state: str = None  # det → tracked → post
    # extra: Dict = field(default_factory=dict)
    @property
    def poly(self):
        rect = ((self.cx, self.cy), (self.w, self.h), self.angle * 180 / np.pi)
        return cv.boxPoints(rect).tolist()
    def to_dict(self, frame_id: int):

        d = self.__dict__.copy()
        d['frame_id'] = frame_id
        d['poly'] = self.poly  # 导出时包含多边形顶点
        return d

class FrameData:
    def __init__(self, frame_id, timestamp=None):
        self.frame_id = frame_id
        self.timestamp = timestamp
        self.objects: List[Obj] = []
    def to_list(self) -> List[Dict]:
        return [obj.to_dict(self.frame_id) for obj in self.objects]