import sqlalchemy
import sqlalchemy.engine
from sqlalchemy.engine.url import URL

from fyoo.resource import FyooResource


# pylint: disable=abstract-method,attribute-defined-outside-init
class DatabaseResource(FyooResource):

    def open(self, **config) -> sqlalchemy.engine.Connection:
        url = URL(self.name, **config)
        engine = sqlalchemy.create_engine(url)
        self.connection = engine.connect()
        return self.connection

    def close(self):
        self.connection.close()
