class StabilizationConfigAdapter:
    def __init__(self, stage_cfg: dict):
        self.cfg = stage_cfg
        
    def get_algorithm_params(self) -> dict:
        
        algo_cfg = self.cfg.get("algorithm", {})
        detector_type = algo_cfg.get("detector", "harris")
        descriptor_type = algo_cfg.get("descriptor", "orb")
        matcher_type = algo_cfg.get("matcher", "bf")
        motion_model_type = algo_cfg.get("motion_model", "homography")
        ransac_method = algo_cfg.get("ransac_method", "usac_magsac")

        params = {}

        # ---------------------
        # Detector params
        # ---------------------
        detector_params = self.cfg.get("detectors", {}).get(detector_type, {})
        params.update(detector_params)

        # ---------------------
        # Descriptor params
        # ---------------------
        descriptor_params = self.cfg.get("descriptors", {}).get(descriptor_type, {})
        params.update(descriptor_params)

        # ---------------------
        # Matcher params
        # ---------------------
        matcher_params = self.cfg.get("matchers", {}).get(matcher_type, {})
        params.update(matcher_params)

        # ---------------------
        # Motion model / RANSAC params
        # ---------------------
        motion_params = self.cfg.get("motion_models", {}).get(motion_model_type, {})
        params.update(motion_params)
        params["ransac_method"] = ransac_method

        # ---------------------
        # Global param
        # ---------------------
        global_param = self.cfg.get("param", {})
        params.update(global_param)
        # ---------------------
        # Mode param
        # ---------------------
        # mode_param = self.cfg.get("mode", {})
        # params.update(mode_param)

        return params