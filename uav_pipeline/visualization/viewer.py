import cv2 as cv
import pandas as pd
import numpy as np
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn
from pathlib import Path
import threading

app = FastAPI()

class StreamState:
    """全局状态管理，用于响应前端的按键指令"""
    def __init__(self, video_path, data_path):
        self.cap = cv.VideoCapture(video_path)
        self.df = pd.read_parquet(data_path) if data_path.endswith('parquet') else pd.read_json(data_path)
        self.frame_id = 0
        self.total_frames = int(self.cap.get(cv.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        self.scale = 1280 / self.cap.get(cv.CAP_PROP_FRAME_WIDTH) # 默认缩放到 720P
        self.is_playing = False
        self.lock = threading.Lock()

    def get_frame(self):
        with self.lock:
            self.cap.set(cv.CAP_PROP_POS_FRAMES, self.frame_id)
            ret, frame = self.cap.read()
            if not ret: return None
            
            # 缩放底图
            h, w = frame.shape[:2]
            frame_draw = cv.resize(frame, (1280, int(h * self.scale)))
            
            # 绘图逻辑
            curr_df = self.df[self.df['frame_id'] == self.frame_id]
            for _, row in curr_df.iterrows():
                poly = (np.array(row['poly']) * self.scale).astype(np.int32).reshape((-1, 1, 2))
                color = (0, 255, 0) if row['state'] == 'det' else (0, 165, 255)
                cv.polylines(frame_draw, [poly], True, color, 2)
                label = f"{row['state']} {int(row['label'])}"
                cv.putText(frame_draw, label, tuple(poly[0][0]), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # 叠加 Frame ID 信息
            cv.putText(frame_draw, f"Frame: {self.frame_id}/{self.total_frames}", (20, 40), 
                       cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            _, jpeg = cv.imencode('.jpg', frame_draw)
            return jpeg.tobytes()

# 实例化全局状态
# 注意：实际工程中可以从环境变量或启动参数获取路径
state = StreamState(
    video_path="/mnt/DataBackup/Workspace/Docker/UAV/uav_pipeline/workdir/jobs/output_20260130_8d53e1aa/stabilization/output_stabi.MP4",
    data_path="/mnt/DataBackup/Workspace/Docker/UAV/uav_pipeline/workdir/jobs/output_20260130_8d53e1aa/detection/det_res.json"
)

@app.get("/video_feed")
async def video_feed():
    """视频流端点"""
    def generate():
        while True:
            frame_bytes = state.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
            if state.is_playing:
                state.frame_id = min(state.frame_id + 1, state.total_frames - 1)
            # 控制流速
            import time
            time.sleep(0.03)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/ctrl/{cmd}")
async def control(cmd: str):
    """前端指令接收端点"""
    if cmd == "next": state.frame_id = min(state.frame_id + 1, state.total_frames - 1)
    elif cmd == "prev": state.frame_id = max(0, state.frame_id - 1)
    elif cmd == "play": state.is_playing = not state.is_playing
    return {"frame_id": state.frame_id}

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页：包含视频显示和键盘监听逻辑"""
    return """
    <html>
        <body style="background: #111; color: white; text-align: center; font-family: sans-serif;">
            <h1>🚁 UAV Pipeline Web Viewer</h1>
            <img src="/video_feed" style="width: 80%; border: 2px solid #444;">
            <div style="margin-top: 20px;">
                <p>使用键盘按键进行操作：</p>
                <p><b>空格</b>: 播放/暂停 | <b>→</b>: 下一帧 | <b>←</b>: 上一帧</p>
            </div>
            <script>
                document.addEventListener('keydown', function(e) {
                    if(e.code === 'ArrowRight') fetch('/ctrl/next');
                    if(e.code === 'ArrowLeft') fetch('/ctrl/prev');
                    if(e.code === 'Space') fetch('/ctrl/play');
                });
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)