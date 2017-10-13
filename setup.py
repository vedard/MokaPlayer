import glob
import os

from setuptools import setup, find_packages

_install_requires = [
    'pyyaml',
    'appdirs',
    'peewee',
    'requests',
    'lxml',
    'arrow',
    'appdirs',
    'pytaglib'
]

_data_files = [
    ('share/applications', ['musicplayer/data/musicplayer.desktop'])
]

for path in glob.glob('musicplayer/data/icons/hicolor/*x*'):
    folder = os.path.basename(path)
    _data_files.append((f'share/icons/hicolor/{folder}/apps', [f'{path}/apps/musicplayer.png']))

setup(
    name="MusicPlayer",
    version="2.0.0.0",
    packages=find_packages(exclude=["test"]),
    author="Vincent Bédard",
    description="A simple music player",
    url="https://github.com/vedard/MusicPlayer/",
    license="MIT",
    keywords="music player tags tabs lyrics",
    entry_points={
        'console_scripts': [
            'musicplayer=musicplayer:main',
        ],
    },
    data_files=_data_files,
    zip_safe=False,
    install_requires=_install_requires,
    include_package_data=True,
)
