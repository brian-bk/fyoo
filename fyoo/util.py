import os
import json
import re
from argparse import Action, ArgumentTypeError
from configparser import SafeConfigParser
from typing import Dict, List, Optional, Text

CONFIG_ENV_VAR_REGEX = r'|'.join([
    r'^FYOO_',
    r'^PATH$',
    r'^PYTHONPATH$',
    r'^PWD$',
    r'^HOME$',
    r'^USER$',
])


def csv_list_type(value: Optional[Text] = None) -> List[Text]:
    if not value:
        return []
    return [v for v in value.split(',') if v]


def read_config(config_filename: Text) -> Dict[Text, Dict]:
    regex = re.compile(CONFIG_ENV_VAR_REGEX, flags=re.IGNORECASE)
    env_vars = {
        key: value
        for key, value in os.environ.items()
        if regex.match(key)
    }
    config = SafeConfigParser(env_vars)
    config.read([config_filename, ])
    config_dict = {
        section_key: {
            item_key: item_value
            for item_key, item_value in dict(section_value).items()
            if not regex.match(item_key)
        }
        for section_key, section_value in dict(config).items()
    }
    return config_dict


def json_dict_type(value: Optional[Text] = None):
    if not value:
        return {}
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ArgumentTypeError('JSON contents should explicitly be a dictionary')
    return data


# pylint: disable=too-few-public-methods
class NegateAction(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, option_string[2:4] != 'no')
