
import importlib
import modulefinder
import os
import pkgutil
import sys
from logging import getLogger

from fyoo.parser import ParserSingleton

logger = getLogger(__name__)

FLOW_DIRECTORIES = [f for f in os.getenv('FYOO__FLOW_DIRECTORIES', '').split(',') if f]


def import_submodules(package, recursive=True):
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    if hasattr(package, '__path__'):
        for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + '.' + name
            try:
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
            if os.path.isfile(filename) and not os.path.isdir(filename) and filename.endswith('.py'):
                module_finder.load_file(filename)


def get_parser():
    parser_singleton = ParserSingleton.instance()
    import_submodules('fyoo.ext')
    return parser_singleton.parser


def main():
    parser_singleton = ParserSingleton.instance()

    import_submodules('fyoo.ext')
    for flow_directory_to_scan in FLOW_DIRECTORIES:
        import_from_path(flow_directory_to_scan)

    parser_singleton.main(sys.argv)
