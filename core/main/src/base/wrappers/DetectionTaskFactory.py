from typing import Type
from core.main.src.base.wrappers.AbstractDetectionTask import AbstractDetectionTask
from core.main.src.wrappers.DetectionTask import DetectionTask

class DetectionTaskFactory:
    """
    Factory for creating detection task instances.
    Extend this class to register and instantiate different DetectionTask types.
    """
    _registry = {
        'default': DetectionTask,
        # Add other detection task types here as needed
    }

    @classmethod
    def register_task_type(cls, key: str, task_cls: Type[AbstractDetectionTask]):
        cls._registry[key] = task_cls

    @classmethod
    def create(cls, task_type: str = 'default', *args, **kwargs) -> AbstractDetectionTask:
        if task_type not in cls._registry:
            raise ValueError(f"Unknown DetectionTask type: {task_type}")
        return cls._registry[task_type](*args, **kwargs)
