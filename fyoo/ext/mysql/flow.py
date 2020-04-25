import argparse

import fyoo
from fyoo.ext.mysql.resource import MysqlResource
from fyoo.ext_base.db.util import db_query_to_csv_file


@fyoo.argument('--query-batch-size', type=int, default=10_000)
@fyoo.argument('target', type=argparse.FileType('w'), help='Target output CSV file')
@fyoo.argument('sql')
@fyoo.resource(MysqlResource)
@fyoo.flow()
def mysql_query_to_csv_file(**kwargs) -> None:
    db = kwargs.pop('mysql')
    return db_query_to_csv_file(db=db, **kwargs)
