from argparse import ArgumentParser, Namespace
from typing import Callable, Optional, Sequence, Text

import jinja2


class FlowParser(ArgumentParser):

    def __init__(self, *args, func: Optional[Callable] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.func = func

    # pylint: disable=arguments-differ
    def parse_known_args(
            self,
            args: Sequence[Text] = None,
            namespace: Namespace = None,
            jinja_env: Optional[jinja2.Environment] = None
    ):
        if args is not None and jinja_env is not None:
            args = [
                jinja_env.from_string(arg).render()
                for arg in args
            ]
        parsed_args, unknown_args = super().parse_known_args(args=args, namespace=namespace)

        return parsed_args, unknown_args
