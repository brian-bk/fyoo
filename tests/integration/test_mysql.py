from collections import OrderedDict
import csv
import tempfile

from fyoo.cli import main


def test_basic_query_to_csv_file():
    with tempfile.NamedTemporaryFile() as td:
        main([
            'mysql_query_to_csv_file',
            'select 1 as a',
            str(td.name),
        ])
        with open(td.name, 'r') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            assert [OrderedDict([('a', '1')])] == rows
            assert [OrderedDict([('a', '2')])] != rows

