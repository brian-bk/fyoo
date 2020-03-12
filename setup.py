import codecs
import itertools
import os
import re
from typing import List

from setuptools import find_packages, setup
from setuptools.command.install import install

HERE = os.path.abspath(os.path.dirname(__file__))


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


def read_code(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'r') as fp:
        return fp.read()


def find_version():
    version_file = read_code('fyoo', '__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def install_requires():
    return [
        'configparser',
        'jinja2',
    ]


def extras_require():
    database_common_requires = ['sqlalchemy']
    require = {
        'mysql': ['mysqlclient'] + database_common_requires,
        'postgres': ['psycopg2'] + database_common_requires,
        'test': [
            'pylint',
            'pytest',
            'pytest-cov',
            'pytest-env',
        ],
    }
    dev_requires = {
        'autopep8',
        'codecov',
        'coverage',
        'twine',
        'sphinx',
        'sphinx-autobuild',
        'sphinx_rtd_theme',
        'sphinx-argparse',
    }
    dev_requires.update(set(require['test']))  # dev tooling always needs test tooling
    require = dict(**require, dev=dev_requires)  # add in 'dev' extra
    # Ensure that all always has everything
    all_requires = list(set(
        itertools.chain.from_iterable(require.values())
    ))
    return dict(**require, all=all_requires)


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')
        version = find_version()

        if tag != version:
            raise RuntimeError(f'Git tag: {tag} does not match the version of this app: {version}')


def do_setup():
    setup(
        name='fyoo',
        version=find_version(),
        long_description=read('README.rst'),
        packages=find_packages(exclude=['tests*']),
        install_requires=install_requires(),
        extras_require=extras_require(),
        entry_points={
            'console_scripts': [
                'fyoo = fyoo.cli:main',
            ],
        },
        python_requires='>=3.7',
        cmdclass={
            'verify': VerifyVersionCommand,
        }
    )


if __name__ == '__main__':
    do_setup()
