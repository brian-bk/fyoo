import os
import re
from abc import abstractmethod
from argparse import Action
from configparser import SafeConfigParser
from typing import Any, Dict, List, Optional

CONFIG_ENV_VAR_REGEX = r'|'.join([
    r'^FYOO',
    r'^PATH$',
    r'^PYTHONPATH$',
    r'^PWD$',
    r'^HOME$',
    r'^USER$',
])


def csv_list_type(value: Optional[str] = None) -> List[str]:
    if not value:
        return []
    return [v for v in value.split(',') if v]


def config_parser_type(value: Optional[str] = None) -> Dict[str, Dict]:
    if value:
        paths = [v for v in value.split(',') if v]
    else:
        paths = ['fyoo.ini', ]
    regex = re.compile(CONFIG_ENV_VAR_REGEX, flags=re.IGNORECASE)
    env_vars = {
        key: value
        for key, value in os.environ.items()
        if regex.match(key)
    }
    config = SafeConfigParser(env_vars)
    config.read(paths)
    config_dict = {
        section_key: {
            item_key: item_value
            for item_key, item_value in dict(section_value).items()
            if not regex.match(item_key)
        }
        for section_key, section_value in dict(config).items()
    }
    return config_dict


# pylint: disable=too-few-public-methods
class NegateAction(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, option_string[2:4] != 'no')


class Singleton:

    _instance = None

    @abstractmethod
    def __init__(self):
        raise NotImplementedError()

    def __new__(cls, **kwargs) -> Any:
        if kwargs.pop('_is_instance_call', False) is not True:
            raise ValueError(f'Not calling instance for {cls}')
        return super(Singleton, cls).__new__(cls)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls, _is_instance_call=True)  # pylint: disable=too-many-function-args
            cls._instance.__init__()
        return cls._instance
