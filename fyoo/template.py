from datetime import datetime

from jinja2.environment import Environment
from jinja2.ext import Extension


class DatetimeExtension(Extension):

    def __init__(self, environment: Environment):
        super().__init__(environment)
        environment.globals['now'] = self.now
        environment.globals['date'] = self.date

    def parse(self, parser):
        pass

    @classmethod
    def now(cls, tz=None) -> datetime:
        """
        Call datetime.datetime.now.

        .. code-block:: bash

            fyoo hello --message '{{ now().isoformat() }}
            # 2020-02-27T21:32:22.190776
        """
        return datetime.now(tz=tz)

    @classmethod
    def date(cls, fmt=r'%Y-%m-%d') -> str:
        """
        Get the current formatted datetime.

        .. code-block:: bash

            fyoo hello --message '{{ date() }}'
            # 2020-02-27

            fyoo hello --message '{{ date("%Y") }}'
            # 2020

        """
        return datetime.now().strftime(fmt)
