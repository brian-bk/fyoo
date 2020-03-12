import sqlalchemy
import sqlalchemy.engine
from sqlalchemy.engine.url import URL

from fyoo.resource import FyooResource


# pylint: disable=abstract-method
class DatabaseResource(FyooResource):

    def open(self, **config) -> sqlalchemy.engine.Connection:
        url = URL(self.name, **config)
        engine = sqlalchemy.create_engine(url)
        return engine

    def close(self, asset: sqlalchemy.engine.Connection) -> None:
        asset.dispose()
