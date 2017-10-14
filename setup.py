import glob
import os

from setuptools import setup, find_packages
import mokaplayer
import os
import re

def get_version():
    with open('mokaplayer/__init__.py') as f:
        version_match = re.search(r"__version__ = '(.*)'", f.read())
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")

def get_data_files():
    yield ('share/applications', ['mokaplayer/data/mokaplayer.desktop'])

    for path in glob.glob('mokaplayer/data/icons/hicolor/*x*'):
        folder = os.path.basename(path)
        yield (f'share/icons/hicolor/{folder}/apps', [f'{path}/apps/mokaplayer.png'])

setup(
    name="MokaPlayer",
    license="MIT",
    version=get_version(),
    author="Vincent Bédard",
    description="A simple music player",
    keywords="mokaplayer music player tags tabs lyrics",
    url="https://github.com/vedard/MokaPlayer/",
    packages=find_packages(exclude=["test"]),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'pyyaml',
        'appdirs',
        'peewee',
        'requests',
        'lxml',
        'arrow',
        'appdirs',
        'pytaglib'
    ],
    data_files= list(get_data_files()),
    entry_points={
        'console_scripts': [
            'mokaplayer=mokaplayer:main',
        ],
    },
)
