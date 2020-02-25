from datetime import datetime

from jinja2.environment import Environment
from jinja2.ext import Extension


class DatetimeExtension(Extension):

    def __init__(self, environment: Environment):
        super().__init__(environment)
        environment.globals['datetime'] = self.datetime
        environment.globals['date'] = self.date

    def parse(self, parser):
        pass

    @classmethod
    def datetime(cls):
        return datetime

    @classmethod
    def date(cls, fmt=r'%Y-%m-%d') -> str:
        return datetime.now().strftime(fmt)
