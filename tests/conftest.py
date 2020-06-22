from unittest.mock import patch

import pytest

from fyoo.cli import CliSingleton


@pytest.fixture(autouse=True)
def clear_cli_singleton():
    yield
    CliSingleton.remove()


@pytest.fixture(autouse=True)
def os_execvp():
    with patch('os.execvp') as patched:
        yield patched
