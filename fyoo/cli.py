import argparse
import importlib
import modulefinder
import os
import sys
import pkgutil
from logging import getLogger
import traceback
from typing import Callable, Dict, List, Optional, Sequence, Set, Text, Tuple

import jinja2

from fyoo.exception import FyooRuntimeException
from fyoo.resource import FyooResource
from fyoo.parser import FlowParser
from fyoo.util import (
    csv_list_type,
    json_dict_type,
    read_config,
    NegateAction,
)

logger = getLogger(__name__)

FLOW_DIRECTORIES = [f for f in os.getenv('FYOO__FLOW_DIRECTORIES', '').split(',') if f]


def import_submodules(package, recursive=True):
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    if hasattr(package, '__path__'):
        logger.debug('Checking package with paths %s', package.__path__)
        for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + '.' + name
            try:
                logger.debug('Importing module %s', full_name)
                results[full_name] = importlib.import_module(full_name)
                if recursive and is_pkg:
                    results.update(import_submodules(full_name))
            # pylint: disable=broad-except
            except Exception as e:
                logger.debug('Had exception when loading module %s: %s', full_name, e)
    return results


def import_from_path(path):

    module_finder = modulefinder.ModuleFinder()
    for folder, _, files in os.walk(path):
        for file in files:
            filename = os.path.join(folder, file)
            logger.debug('Considering import of file %s', filename)
            if os.path.isfile(filename) and not os.path.isdir(filename) and filename.endswith('.py'):
                logger.debug('Importing file %s', filename)
                module_finder.load_file(filename)


class CliSingleton:

    __instance = None

    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()
        self._jinja_env = jinja2.Environment()
        self._subparsers = self._parser.add_subparsers(parser_class=FlowParser)
        self._flows: Dict[str, FlowParser] = dict()

        self._parser.add_argument('--resource-config', default=os.getenv('FYOO_RESOURCE_CONFIG', os.path.join(os.getcwd(), 'fyoo.ini')),
                                  help='The resource configuration file to use')
        self.resource_config = dict()
        self._parser.add_argument('--jinja-strict', '--no-jinja-strict', dest='jinja_strict',
                                  action=NegateAction, nargs=0, default=True,
                                  help='Whether to be strict about undefined jinja variables (default: ON)')
        self._parser.add_argument('--jinja-context', default=json_dict_type(), type=json_dict_type,
                                  help='Extra JSON context argument templating at runtime')
        self._parser.add_argument('--jinja-extensions', default=csv_list_type(), type=csv_list_type,
                                  help='Extra jinja extensions to use')

    def _cb_resource_config(self, value: Text):
        self.resource_config = read_config(value)

    def _cb_jinja_strict(self, value: bool):
        if value:
            self._jinja_env.undefined = jinja2.StrictUndefined

    def _cb_jinja_context(self, value: dict):
        self._jinja_env.globals.update(value)

    def _cb_jinja_extensions(self, value: Sequence[Text]):
        for jinja_extension in value:
            self._jinja_env.add_extension(jinja_extension)

    def add_flow(self, prog: str, func: Callable, **kwargs):
        _flow: argparse.ArgumentParser = self._subparsers.add_parser(prog, func=func, **kwargs)
        if not isinstance(_flow, FlowParser):
            raise RuntimeError('Flow is somehow not a FlowParser')
        flow: FlowParser = _flow
        flow.set_defaults(flow=flow)
        self._flows[prog] = flow

    def get_flow(self, prog: str) -> FlowParser:
        return self._flows[prog]

    def main(self, args: Sequence[Text]):
        action_dests: Set[Text] = {
            action.dest
            for action in self._parser._actions  # pylint: disable=protected-access
            if action.dest != argparse.SUPPRESS and action.dest != 'help'
        }

        preprocessed_parsed_args = self._parser.parse_args(args=args)

        self._subparsers.required = True
        flow: FlowParser = preprocessed_parsed_args.flow

        # do some stuff
        for action_dest in action_dests:
            if hasattr(self, f'_cb_{action_dest}'):
                callback: Callable = getattr(self, f'_cb_{action_dest}')
                callback(getattr(preprocessed_parsed_args, action_dest))

        parsed_args, _ = flow.parse_known_args(args=[
            arg for arg in args
            if arg not in self._subparsers.choices.keys()
        ], jinja_env=self._jinja_env)
        kwargs = dict()

        try:
            fyoo_resources: List[FyooResource] = list()
            for key, value in vars(parsed_args).items():
                if key in action_dests or key == 'flow':
                    continue
                if isinstance(value, FyooResource):
                    fyoo_resources.append(value)
                    kwargs[key] = value.open(**self.resource_config[key])
                else:
                    kwargs[key] = value
            flow.func(**kwargs)
            for fyoo_resource in fyoo_resources:
                fyoo_resource.close()
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
                logger.error('%d errors happened when closing FyooResources', len(formatted_exceptions))
                for formatted_exception in formatted_exceptions:
                    logger.error('%s closure exception: %s',
                                 formatted_exception[0].identifier, formatted_exception[1])
                raise FyooRuntimeException('Had exceptions closing FyooResources')

    def __new__(cls, **kwargs):
        if kwargs.pop('_is_instance_call', False) is not True:
            raise ValueError(f'Not calling instance for {cls}')
        return super(CliSingleton, cls).__new__(cls)

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = cls.__new__(cls, _is_instance_call=True)  # pylint: disable=too-many-function-args
            cls.__instance.__init__()
        return cls.__instance


def get_parser():
    import_submodules('fyoo.ext')
    return CliSingleton.instance()._parser


def main(args: Optional[Sequence[Text]] = None):
    if args is None:
        args = sys.argv[1:]
    cli = CliSingleton.instance()

    import_submodules('fyoo.ext')
    for flow_directory_to_scan in FLOW_DIRECTORIES:
        import_from_path(flow_directory_to_scan)

    cli.main(args)


if __name__ == '__main__':
    main()
