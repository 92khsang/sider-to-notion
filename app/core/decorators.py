from __future__ import annotations


def singleton(cls):
    """A decorator that turns a class into a singleton by overriding __new__."""
    instances: dict[type, object] = {}
    orig_new = cls.__new__

    def new(clz, *args, **kwargs):
        if clz not in instances:
            instances[clz] = orig_new(clz, *args, **kwargs)
        return instances[clz]

    cls.__new__ = new
    return cls
