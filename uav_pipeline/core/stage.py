import os
import json
from uav_pipeline.core.artifact import Artifact
from uav_pipeline.core.schema import FrameData
import pandas as pd
from pathlib import Path
from typing import List
class Stage:
    stage_name: str = None

    def run(self, ctx):
        raise NotImplementedError("Stage must implement run(ctx)")
    
    def mock(self, ctx):
        manifest_path = os.path.join(ctx.workdir, "manifest.json")

        if not os.path.exists(manifest_path):
            ctx.logger.warning("No manifest found, fallback to run()")
            self.run(ctx)
            return
        with open(manifest_path) as f:
            manifest = json.load(f)

        restored = 0
        for item in manifest.get("artifacts", []):
            if item["stage"] != self.stage_name:
                continue

            local_path = item["local_path"]

            if not os.path.exists(local_path):
                ctx.logger.warn(f"Artifact missing on disk: {local_path}")
                continue

            artifact = Artifact(
                stage=item["stage"],
                name=item["name"],
                kind=item["kind"],
                local_path=item["local_path"],
                meta=item["meta"],
                persistent= item["persistent"]
            )
            ctx.artifacts_register.register(artifact,write_mode=False)
            restored += 1

        if restored == 0:
            ctx.logger.warn(f"No artifacts restored for {self.__class__.__name__}, running stage")
            self.run(ctx)
        else:
            ctx.logger.info(f"[DEBUG] Restored {restored} artifacts for {self.__class__.__name__}")

    def save_results(self, res: List[FrameData], stage_dir: Path, base_name: str = "results"):
        # 1. 展平数据
        rows = []
        for f in res:
            rows.extend(f.to_list())
        
        df = pd.DataFrame(rows)
        
        # 2. 保存 Parquet (高性能)
        parquet_path = stage_dir / f"{base_name}.parquet"
        df.to_parquet(parquet_path, index=False)
        
        # 3. 保存 JSON (可读性好)
    
        json_path = stage_dir / f"{base_name}.json"
        df.to_json(json_path, orient='records', indent=4, force_ascii=False)
        
        return parquet_path, json_path

    