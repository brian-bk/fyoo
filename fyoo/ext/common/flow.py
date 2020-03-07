from pathlib import Path
import shutil

import fyoo


@fyoo.argument('--message', help='Message to print out')
@fyoo.flow()
def hello(
        message: str,
) -> None:
    print(message)


@fyoo.argument('filename')
@fyoo.flow()
def touch(
        filename: str,
) -> str:
    path = Path(filename)
    path.touch()
    return str(path.absolute())


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
