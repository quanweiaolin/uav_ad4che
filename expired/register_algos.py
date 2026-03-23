from uav_pipeline.stages.stabilization.tools.detectors import HarrisDetector, SIFTDetector
from uav_pipeline.stages.stabilization.tools.matchers import BFMatcher, FLANNMatcher
from uav_pipeline.core.algo_registry import algo_registry

def register_algos():
    algo_registry.register("harris", HarrisDetector)
    algo_registry.register("sift", SIFTDetector)
    algo_registry.register("bf", BFMatcher)
    algo_registry.register("flann", FLANNMatcher)