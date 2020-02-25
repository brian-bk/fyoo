import importlib
import json
import traceback
from argparse import ArgumentParser
from datetime import datetime
from logging import getLogger
from time import time
from typing import Any, Callable, Dict, List, Tuple

from jinja2 import Environment, StrictUndefined

from .exception import FyooJsonException, FyooRuntimeException
from .resource import FyooResource
from .template import DatetimeExtension
from .util import NegateAction, Singleton, config_parser_type, csv_list_type

LOGGER = getLogger(__name__)


class ParserSingleton(Singleton):

    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        self.parser: ArgumentParser = ArgumentParser()
        self.subparsers = self.parser.add_subparsers()
        self.subparsers.dest = 'flow'

        self.flows: Dict[str, ArgumentParser] = {}

        self.parser.add_argument('--flow-config', default=config_parser_type(), type=config_parser_type)
        self.parser.add_argument('--flow-report-file', default=None, type=str)
        self.parser.add_argument('--jinja-strict', '--no-jinja-strict', dest='jinja_strict',
                                 action=NegateAction, nargs=0, default=True)
        self.parser.add_argument('--jinja-context', default=json.loads(r'{}'), type=json.loads)
        self.parser.add_argument('--jinja-extensions', default=csv_list_type(), type=csv_list_type)

    def add_flow(self, func: Callable) -> None:
        parser = self.subparsers.add_parser(func.__name__)
        parser.set_defaults(func=func)
        self.flows[func.__name__] = parser

    def get_flow(self, func: Callable) -> ArgumentParser:
        return self.flows[func.__name__]

    def main(self, sys_args):
        args = self.parser.parse_args(sys_args[1:])

        func = args.__dict__.pop('func')

        jinja_env = Environment()
        if args.__dict__.pop('jinja_strict'):
            jinja_env.undefined = StrictUndefined
        jinja_env.globals.update(args.__dict__.pop('jinja_context'))
        flow_metadata = {
            'name': args.__dict__.pop('flow'),
            'file': importlib.import_module(func.__module__).__file__,
        }
        jinja_env.globals.update({
            'flow': flow_metadata,
        })
        jinja_env.add_extension(DatetimeExtension)
        for extra_jinja_extension in args.__dict__.pop('jinja_extensions'):
            jinja_env.add_extension(extra_jinja_extension)

        kwargs: Dict[str, Any] = {}
        flow_config = args.__dict__.pop('flow_config')
        flow_report_file = jinja_env.from_string(args.__dict__.pop('flow_report_file', None) or '').render()

        try:
            fyoo_resources = []
            for arg_name, arg_value in args.__dict__.items():
                if isinstance(arg_value, FyooResource):
                    fyoo_resources.append(arg_value)
                    fyoo_resource_config = flow_config.get(arg_value.identifier, {})
                    kwargs[arg_name] = arg_value.open(**fyoo_resource_config)
                elif isinstance(arg_value, str):
                    kwargs[arg_name] = jinja_env.from_string(arg_value).render()
                else:
                    kwargs[arg_name] = arg_value

            start_time = time()
            result = func(**kwargs)
            end_time = time()
            report = {
                'metadata': {
                    'start': datetime.fromtimestamp(start_time).isoformat(),
                    'end': datetime.fromtimestamp(end_time).isoformat(),
                    'duration': end_time - start_time,
                    'flow': flow_metadata,
                },
                'kwargs': kwargs,
                'result': result,
            }
            if flow_report_file:
                try:
                    with open(flow_report_file, 'w') as f:
                        json.dump(report, f)
                except TypeError as e:
                    raise FyooJsonException(f'Unable to serialize flow output {e}')
        finally:
            formatted_exceptions: List[Tuple[FyooResource, str]] = []
            for fyoo_resource in fyoo_resources:
                if fyoo_resource.opened:
                    try:
                        fyoo_resource.close()
                    # pylint: disable=bare-except
                    except:
                        formatted_exceptions.append((fyoo_resource, traceback.format_exc()))
            if formatted_exceptions:
                LOGGER.error('%d errors happened when closing FyooResources', len(formatted_exceptions))
                for formatted_exception in formatted_exceptions:
                    LOGGER.error('%s closure exception: %s',
                                 formatted_exception[0].identifier, formatted_exception[1])
                raise FyooRuntimeException('Had exceptions closing FyooResources')
