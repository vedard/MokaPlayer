import os
import pathlib


class ProviderLocalFileSystem(object):

    IMAGE_SUFFIXES = ['.JPG', '.JPEG', '.PNG', '.BMP']

    def __init__(self):
        pass

    def get_name(self):
        "Local files"

    def get_album_artwork(self, album_path):
        for file in sorted(pathlib.Path(album_path).glob('*'), key=os.path.getsize, reverse=True):
            if file.suffix.upper() in ProviderLocalFileSystem.IMAGE_SUFFIXES:
                return str(file.absolute())
        return None
