from typing import Type, Dict

class AlgorithmRegistry:
    """全局算法注册器"""
    def __init__(self):
        self._registry: Dict[str, Type] = {}

    def register(self, name: str, cls: Type):
        if name in self._registry:
            raise ValueError(f"Algorithm {name} already registered")
        self._registry[name] = cls

    def get(self, name: str) -> Type:
        if name not in self._registry:
            raise KeyError(f"Algorithm {name} not found")
        return self._registry[name]

    def list(self):
        return list(self._registry.keys())


algo_registry = AlgorithmRegistry()