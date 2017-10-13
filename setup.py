from setuptools import setup, find_packages

setup(
    name="MusicPlayer",
    version="2.1.0.0",
    packages=find_packages(exclude=["test"]),
    author="Vincent Bédard",
    author_email="vedard@gmail.com",
    description="A simple music player",
    license="MIT",
    keywords="music player tags tabs lyrics",
    entry_points={
        'console_scripts': [
            'musicplayer=musicplayer:main',
        ],
    },
    data_files=[
        ('share/applications', ['musicplayer/resources/musicplayer.desktop']),
        ('share/musicplayer', ['musicplayer/resources/icon.png']),
    ],
    install_requires=['pyyaml',
                      'appdirs',
                      'peewee',
                      'requests',
                      'lxml',
                      'arrow',
                      'appdirs'
                      ],
    include_package_data=True,
    url="https://github.com/vedard/MusicPlayer/",
)
