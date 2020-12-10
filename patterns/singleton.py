from typing import Dict, Any


class Singleton(type):
    _instances: Dict['Singleton', 'Singleton'] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> 'Singleton':
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
