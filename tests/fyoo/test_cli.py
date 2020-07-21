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


def test_fyoo_context_auto_format(os_execvp):
    main([r'--context={"a": {"b": "AAA"}}', '--', 'echo', '-n', r'{{ a.b }} {{ date() }}'])
    os_execvp.assert_called_once_with('echo', ['echo', '-n', f'AAA {TODAY_DT_DS}'])


@pytest.mark.parametrize('context,context_format,expected_exception_cls', [
    ('a: AAA', 'json', json.decoder.JSONDecodeError),
])
def test_fyoo_context_wrong_format(context, context_format, expected_exception_cls):
    with pytest.raises(expected_exception_cls):
        main([
            f'--context={context}', f'--context-format={context_format}', '--',
            'echo', '-n', r'{{ a }} {{ date() }}'
        ])


def test_fyoo_context_bad_format():
    with pytest.raises(ValueError):
        main([
            f'--context=a: b: 333', '--',
            'echo', '-n', r'{{ a }} {{ date() }}'
        ])


def test_fyoo_dry_run_stops(os_execvp):
    main([
        f'--dry-run', '--',
        'echo', '-n', 'hello'
    ])
    os_execvp.assert_not_called()


def test_fyoo_command_not_exist_error():
    with pytest.raises(SystemExit):
        main([ '--', 'idontexistascommand'])


def test_double_exec(os_execvp):
    main([f'--', 'echo', '--', '-n', r'{{ a }} {{ date() }}'])
    os_execvp.assert_called_once_with('echo', ['echo', '--', '-n', f' {TODAY_DT_DS}'])


@pytest.mark.subprocess
def test_double_exec_output():
    p = subprocess.run(['fyoo', '--', 'echo', '-n', '--', '-n', r'date is {{ date() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'-- -n date is {TODAY_DT_DS}')


@pytest.mark.subprocess
def test_fyoo_basic_echo():
    p = subprocess.run(['fyoo', '--', 'echo', '-n', r'date is {{ date() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'date is {TODAY_DT_DS}')


@pytest.mark.subprocess
def test_fyoo_echo_pass_context():
    p = subprocess.run(['fyoo', r'--context={"a":{"b": 333}}', '--', 'echo', '-n', r'{{ a.b }} and {{ date() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'333 and {TODAY_DT_DS}')


@pytest.mark.subprocess
def test_fyoo_wrapped_bash():
    p = subprocess.run(['fyoo', r'--context={"a":{"b": 333}}', '--', 'echo', '-n', r'{{ a.b }} and {{ date() }}'], capture_output=True, check=True)
    assert (p.stderr.decode(), p.stdout.decode()) == ('', f'333 and {TODAY_DT_DS}')
