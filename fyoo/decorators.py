import functools
from typing import Optional

from fyoo.parser import ParserSingleton
from fyoo.resource import FyooResource


def flow():
    def d_flow(func):
        ParserSingleton.instance().add_flow(func)

        @functools.wraps(func)
        def f_flow(*args, **kwargs):
            return func(*args, **kwargs)
        return f_flow
    return d_flow


def argument(*dargs, **dkwargs):
    def decorator(func):
        parser = ParserSingleton.instance().get_flow(func)
        parser.add_argument(*dargs, **dkwargs)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped_func
    return decorator


def resource(resource_type: type, *dargs, which: Optional[str] = None, **dkwargs):
    if not issubclass(resource_type, FyooResource):
        raise ValueError('resource_type must be a FyooResource')

    if which is None:
        arg = f'--{resource_type.name}'
    else:
        arg = f'--{resource_type.name}-{which}'

    def decorator(func):
        parser = ParserSingleton.instance().get_flow(func)
        parser.add_argument(arg, *dargs, type=resource_type, default='', **dkwargs)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped_func
    return decorator
