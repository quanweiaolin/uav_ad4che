import json
# from uav_pipeline.core.context import JobContext


class ArtifactManager:
    def __init__(self, storage):
        self.storage = storage

    # def handle(self, artifacts):
    #     for art in artifacts:
    #         if art.persistent:
    #             self.storage.put(
    #                 art.local_path,
    #                 f"{art.kind}/{art.name}"
    #             )

    def finalize_job(self,context):
        manifest = {
            "job_id": context.job_id,
            "artifacts": [
                a.to_dict() for a in context.artifacts_register.list()
            ]
        }

        manifest_path = context.workdir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        for artifact in context.artifacts_register.list():
            if artifact.persistent:
                self.storage.put(artifact)

        # self.cleanup_ephemeral(context)

    # def cleanup_ephemeral(self,context):
    #     for artifact in context.artifacts_register.list():
    #         if artifact.persistent:
    #             self.storage.put(artifact)
        