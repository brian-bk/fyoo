import csv

from sqlalchemy.engine import Connection, ResultProxy

import fyoo
from fyoo.ext.mysql.resource import MysqlResource


@fyoo.argument('--query-batch-size', type=int, default=10_000)
@fyoo.argument('target')
@fyoo.argument('sql')
@fyoo.resource(MysqlResource)
@fyoo.flow()
def mysql_query_to_csv_file(
        mysql: Connection,
        sql: str,
        target: str,
        query_batch_size: int,
):
    result_proxy: ResultProxy = mysql.execute(sql)

    with open(target, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(result_proxy.keys())
        while result_proxy.returns_rows:
            rows = result_proxy.fetchmany(query_batch_size)
            if not rows:
                break
            writer.writerows(rows)
