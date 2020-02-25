from datetime import datetime

from jinja2.environment import Environment
from jinja2.ext import Extension


class DatetimeExtension(Extension):

    def __init__(self, environment: Environment):
        super().__init__(environment)
        environment.globals['datetime'] = datetime

    def parse(self, parser):
        pass
