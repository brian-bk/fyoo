import argparse

import fyoo
from fyoo.ext.postgres.resource import PostgresResource
from fyoo.ext_base.db.util import db_query_to_csv_file


@fyoo.argument('--query-batch-size', type=int, default=10_000)
@fyoo.argument('target', type=argparse.FileType('w'))
@fyoo.argument('sql')
@fyoo.resource(PostgresResource)
@fyoo.flow()
def postgres_query_to_csv_file(**kwargs) -> None:
    db = kwargs.pop('postgres')
    return db_query_to_csv_file(db=db, **kwargs)
