import pytest

from fyoo.parser import FyooParser
from fyoo.exception import FyooTemplateException


def test_template_raw_datetime_strptime():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([r'{{ raw_datetime.strptime("2020", "%Y") }}', ]).first_arg == '2020-01-01 00:00:00'


def test_template_throw_error():
    p = FyooParser()
    p.add_argument('first_arg')

    with pytest.raises(FyooTemplateException, match='Cool Err'):
        p.parse_args([r'{{ throw("Cool Err") }}', ])
