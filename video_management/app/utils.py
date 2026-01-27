import subprocess, json
import boto3
import uuid


s3_client = boto3.client(
            "s3",
            endpoint_url="http://192.168.50.125:9000",
            aws_access_key_id="n0O2iZ2O0Vg5CXkvC9Dg",
            aws_secret_access_key="TMZseFokKYpSyVabBByTXWbE12PCX8gQLKtuNaz6",
            # bucket_name="ad4che"
        )

def extract_video_meta(local_path):
    """用 ffprobe 提取视频技术信息"""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-show_entries", "format=duration,size",
        "-of", "json", local_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(res.stdout)
    stream = info['streams'][0]
    fmt = info['format']
    return {
        "width": int(stream['width']),
        "height": int(stream['height']),
        "fps": eval(stream['r_frame_rate']),
        "duration": float(fmt['duration']),
        "size_mb": float(fmt['size'])/1024/1024
    }

def list_minio_videos(bucket,prefix):
    """列出 MinIO bucket 下所有视频对象"""
    resp = s3_client.list_objects_v2(Bucket=bucket,Prefix=prefix)
    if "Contents" not in resp:
        return []
    # 返回 key 列表
    return [obj["Key"] for obj in resp["Contents"]]