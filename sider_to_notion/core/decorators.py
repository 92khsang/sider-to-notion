from __future__ import annotations

import threading

__all__ = [
    "singleton",
]


def singleton(cls):
    rlock = threading.RLock()
    instances: dict[type, object] = {}
    orig_new = cls.__new__

    def new(clz, *args, **kwargs):
        with rlock:
            if clz not in instances:
                instances[clz] = orig_new(clz, *args, **kwargs)
            return instances[clz]

    cls.__new__ = new
    return cls
