from datetime import datetime
import json
import subprocess

import pytest
from _pytest.capture import CaptureResult
import pytz

from fyoo.cli import main

TODAY_DT_DS = datetime.now(tz=pytz.timezone('UTC')).strftime(r'%Y-%m-%d')


def test_no_arg_fails(capsys):
    with pytest.raises(SystemExit) as e:
        main([])
    out: CaptureResult = capsys.readouterr()
    assert e.value.code == 2
    assert 'Please provide a subcommand' in out.err


def test_unknown_arg_fails(capsys):
    with pytest.raises(SystemExit) as e:
        main(['asdf'])
    out: CaptureResult = capsys.readouterr()
    assert e.value.code == 2
    assert 'invalid choice' in out.err


@pytest.mark.parametrize('context', [
    r'{"a": {"b": "AAA"}}',
    'a:\n b: AAA',
])
def test_fyoo_context_auto_format(context, os_execvp):
    main([f'--fyoo-context={context}', '--', 'echo', '-n', r'{{ a.b }} {{ dt() }}'])
    os_execvp.assert_called_once_with('echo', ['echo', '-n', f'AAA {TODAY_DT_DS}'])


@pytest.mark.parametrize('context,context_format,expected_exception_cls', [
    ('a: AAA', 'json', json.decoder.JSONDecodeError),
])
def test_fyoo_context_wrong_format(context, context_format, expected_exception_cls):
    with pytest.raises(expected_exception_cls):
        main([
            f'--fyoo-context={context}', f'--fyoo-context-format={context_format}', '--',
            'echo', '-n', r'{{ a }} {{ dt() }}'
        ])


def test_fyoo_context_bad_format():
    with pytest.raises(ValueError):
        main([
            f'--fyoo-context=a: b: 333', '--',
            'echo', '-n', r'{{ a }} {{ dt() }}'
        ])


def test_double_exec(os_execvp):
    main([f'--', 'echo', '--', '-n', r'{{ a }} {{ dt() }}'])
    os_execvp.assert_called_once_with('echo', ['echo', '--', '-n', f' {TODAY_DT_DS}'])


@pytest.mark.subprocess
def test_double_exec_output():
    p = subprocess.run(['fyoo', '--', 'echo', '-n', '--', '-n', r'dt is {{ dt() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'-- -n dt is {TODAY_DT_DS}')


@pytest.mark.subprocess
def test_fyoo_basic_echo():
    p = subprocess.run(['fyoo', '--', 'echo', '-n', r'dt is {{ dt() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'dt is {TODAY_DT_DS}')


@pytest.mark.subprocess
def test_fyoo_echo_pass_context():
    p = subprocess.run(['fyoo', '--fyoo-context=a:\n b: 333', '--', 'echo', '-n', r'{{ a.b }} and {{ dt() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'333 and {TODAY_DT_DS}')


@pytest.mark.subprocess
def test_fyoo_wrapped_bash():
    p = subprocess.run(['fyoo', '--fyoo-context=a:\n b: 333', '--', 'echo', '-n', r'{{ a.b }} and {{ dt() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'333 and {TODAY_DT_DS}')
