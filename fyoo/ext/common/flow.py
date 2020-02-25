import shutil

import fyoo
from fyoo.ext.common.resource import DummyResource


@fyoo.argument('--message')
@fyoo.resource(DummyResource)
@fyoo.flow()
def hello(
        message: str,
        dummy: str,
) -> None:
    print(f'Hello {dummy} resource, {message}')
    return 'hello'


@fyoo.argument('target')
@fyoo.argument('source')
@fyoo.flow()
def move(
        target: str,
        source: str,
):
    shutil.move(source, target)


@fyoo.argument('target')
@fyoo.argument('source')
@fyoo.flow()
def copy_file(
        target: str,
        source: str,
):
    shutil.copy(source, target)


@fyoo.argument('target')
@fyoo.argument('source')
@fyoo.flow()
def copy_folder(
        target: str,
        source: str,
):
    shutil.copytree(source, target)
