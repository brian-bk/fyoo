import functools
from typing import Callable, Optional

from fyoo.cli import CliSingleton
from fyoo.resource import FyooResource


def flow() -> Callable:
    """Create a Flow subparser under Fyoo.

    This must be done before arguments or resources
    are decorated on to function. For example:

    .. code-block:: python

        # good
        @resource(PostgresResource)
        @flow
        def my_flow():
            return None

        # bad
        @flow
        @resource(PostgresResource)
        def my_flow():
            return None
    """
    def d_flow(func):
        CliSingleton.instance().add_flow(func.__name__, func)

        @functools.wraps(func)
        def f_flow(*args, **kwargs):
            return func(*args, **kwargs)
        return f_flow
    return d_flow


def argument(*dargs, **dkwargs) -> Callable:
    """Add an argument to the Flow parser, provided to the function as a keyword argument.

    The order of arguments matter, and are added reverse to how they appear
    (they grow from bottom-to-top). This doesn't matter much for optional
    arguments but has significant impact on positional arguments.


    .. code-block:: python

        # good, exposed as positional arguments [SOURCE] [TARGET]
        @argument('target')
        @argument('source')
        @flow
        def my_move_flow():
            return None

        # bad, exposed as positional arguments [TARGET] [SOURCE]
        @argument('source')
        @argument('target')
        @flow
        def my_move_flow():
            return None
    """
    def decorator(func):
        parser = CliSingleton.instance().get_flow(func.__name__)
        parser.add_argument(*dargs, **dkwargs)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped_func
    return decorator


def resource(resource_type: type, *dargs, which: Optional[str] = None, **dkwargs) -> Callable:
    """A short-cut for adding a FyooResource to the Flow subparser.

    Args:
        resource_type (type): [description]
        which (Optional[str], optional): [description]. Defaults to None.

    Raises:
        ValueError: If :arg:`resource_type` is not a subclass of FyooResource

    Returns:
        Callable: [description]
    """
    if not issubclass(resource_type, FyooResource):
        raise ValueError('resource_type must be a FyooResource')

    if which is None:
        arg = f'--{resource_type.name}'
    else:
        arg = f'--{resource_type.name}-{which}'

    def decorator(func):
        parser = CliSingleton.instance().get_flow(func.__name__)
        parser.add_argument(arg, *dargs, type=resource_type, default='', **dkwargs)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped_func
    return decorator
