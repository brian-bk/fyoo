import pytest

from fyoo.parser import FyooParser


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
        '--fyoo-context=a: ABC',
        '--fyoo-context-format=yaml',
        '--fyoo-set=b=DEF',
        '--fyoo-set=c=GHI',
        '--fyoo-jinja-extension=fyoo.internal.template.FyooEnvExtension',
    ])
    assert p.parse_args([]).__dict__ == {}


def test_parser_unrecognized_context_format():
    p = FyooParser()
    with pytest.raises(ValueError, match='idontexist'):
        p.parse_args(['--fyoo-context=a: ABC', '--fyoo-context-format=idontexist', ])


def test_parser_non_dictionary():
    p = FyooParser()
    with pytest.raises(ValueError, match='dictionary'):
        p.parse_args(['--fyoo-context=- a: ABC', '--fyoo-context-format=yaml', ])


def test_unrecognized_extension():
    p = FyooParser()
    with pytest.raises(ModuleNotFoundError):
        p.parse_args(['--fyoo-jinja-extension=i.dont.exist'])


def test_fyoo_context_priority():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--fyoo-context=a: ABC',
        '--fyoo-context=a: DEF',
        r'{{ a }}',
    ]).first_arg == 'DEF'


def test_fyoo_context_set_override():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--fyoo-set=a=GHI',
        '--fyoo-context=a: ABC',
        '--fyoo-context=a: DEF',
        r'{{ a }}',
    ]).first_arg == 'GHI'


def test_fyoo_context_set_override_set():
    p = FyooParser()
    p.add_argument('first_arg')
    assert p.parse_args([
        '--fyoo-set=a=GHI',
        '--fyoo-set=a=JKL',
        '--fyoo-context=a: ABC',
        '--fyoo-context=a: DEF',
        r'{{ a }}',
    ]).first_arg == 'JKL'


def test_fyoo_context_overrides_extension():
    p1 = FyooParser()
    p1.add_argument('first_arg')
    assert 'bound method' in p1.parse_args([
        r'{{ dt }}',
    ]).first_arg

    p2 = FyooParser()
    p2.add_argument('first_arg')
    assert p2.parse_args([
        '--fyoo-set=dt=ABC',
        r'{{ dt }}',
    ]).first_arg == 'ABC'
