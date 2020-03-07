import argparse
import csv
from typing import TextIO

from sqlalchemy.engine import Connection, ResultProxy

import fyoo
from fyoo.ext.postgres.resource import PostgresResource


@fyoo.argument('--query-batch-size', type=int, default=10_000)
@fyoo.argument('target', type=argparse.FileType('w'))
@fyoo.argument('sql')
@fyoo.resource(PostgresResource)
@fyoo.flow()
def postgres_query_to_csv_file(
        postgres: Connection,
        sql: str,
        target: TextIO,
        query_batch_size: int,
):
    result_proxy: ResultProxy = postgres.execute(sql)

    writer = csv.writer(target)
    writer.writerow(result_proxy.keys())
    while result_proxy.returns_rows:
        rows = result_proxy.fetchmany(query_batch_size)
        if not rows:
            break
        writer.writerows(rows)
