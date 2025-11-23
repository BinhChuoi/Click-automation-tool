"""
A module providing a singleton decorator.
"""

def singleton(class_):
    """
    A decorator to implement the singleton pattern.
    """
    instances = {}
    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance
