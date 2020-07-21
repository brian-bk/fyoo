from unittest.mock import patch

import pytest

from jinja2.ext import Extension
import jinja2.exceptions

from fyoo.parser import FyooParser
import fyoo.exception


def test_passed_namespace_no_args_twice():
    """Make sure that parser can parse multiple times.

    (an early implementation added actions multiple times and would break this)
    """
    p = FyooParser()
    assert p.parse_args([]).__dict__ == {}
    assert p.parse_args([]).__dict__ == {}


def test_passed_namespace_no_args_in_this_parser():
    p = FyooParser()
    n = p.parse_args([
        '--context=a: ABC',
        '--context-format=yaml',
        '--set=b=DEF',
        '--set=c=GHI',
    ])
    assert p.parse_args([]).__dict__ == {}


def test_parser_unrecognized_context_format():
    p = FyooParser()
    with pytest.raises(ValueError, match='idontexist'):
        p.parse_args(['--context=a: ABC', '--context-format=idontexist', ])


class TestJinjaExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals['testing'] = 123

    def parse(self, parser):
        pass


def test_jinja_extension():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--jinja-extension=tests.fyoo.test_parser.TestJinjaExtension',
        r'{{ testing }}',
    ]).first_arg == '123'


def test_parser_non_dictionary():
    p = FyooParser()
    with pytest.raises(ValueError, match='dictionary'):
        p.parse_args(['--context=- a: ABC', '--context-format=yaml', ])


def test_unrecognized_extension():
    p = FyooParser()
    with pytest.raises(ModuleNotFoundError):
        p.parse_args(['--jinja-extension=i.dont.exist'])


def test_fyoo_context_priority():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--context={"a":"ABC"}',
        '--context={"a":"DEF"}',
        r'{{ a }}',
    ]).first_arg == 'DEF'


def test_fyoo_context_set_override():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--set=a=GHI',
        '--context={"a":"ABC"}',
        '--context={"a":"DEF"}',
        r'{{ a }}',
    ]).first_arg == 'GHI'


def test_fyoo_context_set_override_set():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--set=a=GHI',
        '--set=a=JKL',
        '--context={"a":"ABC"}',
        '--context={"a":"DEF"}',
        r'{{ a }}',
    ]).first_arg == 'JKL'


def test_fyoo_context_overrides_extension():
    p1 = FyooParser()
    p1.add_argument('first_arg')
    assert 'function' in p1.parse_args([
        r'{{ date }}',
    ]).first_arg

    p2 = FyooParser()
    p2.add_argument('first_arg')
    assert p2.parse_args([
        '--set=date=ABC',
        r'{{ date }}',
    ]).first_arg == 'ABC'


def test_file_loaded_template():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--jinja-template-folder=tests/sql',
        '--set=table=customers',
        r'{% include "count.sql.jinja" %}',
    ]).first_arg.strip() == r'''
select count(*) as c
from customers
'''.strip()


def test_file_loaded_template_throws_explicit_exception():
    p = FyooParser()
    p.add_argument('first_arg')
    with pytest.raises(fyoo.exception.FyooTemplateException):
        p.parse_args([
            '--jinja-template-folder=tests/sql',
            r'{% include "count.sql.jinja" %}',
        ])


def test_file_no_loaded_template_doesnt_exist():
    p = FyooParser()
    p.add_argument('first_arg')
    with pytest.raises(TypeError, match='no loader for this environment specified'):
        p.parse_args([r'{% include "count.sql.jinja" %}'])


def test_file_loaded_template_doesnt_exist():
    p = FyooParser()
    p.add_argument('first_arg')
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        p.parse_args([
            '--jinja-template-folder=tests/sql',
            '--set=table=customers',
            r'{% include "i-dont-exist.sql.jinja" %}',
        ])


def test_implicit_type_boolean():
    p = FyooParser()
    p.add_argument('first_arg')
    p.parse_args([
        '--set=isf=false',
        r'{% if isf %}{% else %}shouldbefalse{% endif %}',
    ]).first_arg == 'shouldbefalse'


def test_implicit_type_boolean_dif_cap():
    p = FyooParser()
    p.add_argument('first_arg')
    p.parse_args([
        '--set=isf=tRuE',
        r'{% if isf %}{% else %}shouldbetrue{% endif %}',
    ]).first_arg == 'True'


def test_implicit_type_int():
    p = FyooParser()
    p.add_argument('first_arg')
    p.parse_args([
        '--set=isi=3',
        r'{{ isi + 1 }}',
    ]).first_arg == '4'


def test_implicit_type_float():
    p = FyooParser()
    p.add_argument('first_arg')
    p.parse_args([
        '--set=isi=3.1',
        r'{{ isi + 1 }}',
    ]).first_arg == '4.1'


def test_set_by_env_var():
    p = FyooParser()
    p.add_argument('first_arg')
    with patch('os.environ', {'FYOO__SET__a': 'somea'}):
        p.parse_args([r'{{ a }}']) == 'somea'
