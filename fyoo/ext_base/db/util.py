import csv
from typing import TextIO

from sqlalchemy.engine import Connection, ResultProxy


def db_query_to_csv_file(
        db: Connection,
        sql: str,
        target: TextIO,
        query_batch_size: int,
) -> None:
    result_proxy: ResultProxy = db.execute(sql)

    writer = csv.writer(target)
    writer.writerow(result_proxy.keys())
    while result_proxy.returns_rows:
        rows = result_proxy.fetchmany(query_batch_size)
        if not rows:
            break
        writer.writerows(rows)
